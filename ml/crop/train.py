"""
Step 2: train the "what is grown here" model and test it on unseen areas.

    python train.py

One LightGBM model per crop predicts the crop's share of farmland in a MapSPAM cell.
Testing uses spatial cross-validation: whole 1°x1° blocks (~110 km) are held out, so
the scores show how well it does somewhere it has not seen, not just next door.

The app averages the model with the shares in the nearest MapSPAM cells (that blend did
best on held-out areas) and combines the result with ECOCROP suitability:
    final = suitability x (alpha + (1 - alpha) x local share / largest local share)
alpha is a choice, not tuned: alpha = 0 scores best at "recommend what is already grown"
but would never suggest a suitable crop that is new to an area. ALPHA keeps both.

Writes runs/<timestamp>/metrics.json and installs the model into
crop_recommendation/crop_predictor/ml_models/prevalence/.
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.neighbors import KNeighborsRegressor

HERE = Path(__file__).parent
APP = HERE.parents[1] / "crop_recommendation"
sys.path.insert(0, str(APP))
from crop_predictor import prevalence, suitability  # noqa: E402

LABELS = list(prevalence.LABELS)
PARAMS = dict(objective="cross_entropy", n_estimators=300, learning_rate=0.05, num_leaves=31,
              min_child_samples=30, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, verbose=-1)
ALPHAS = [0.0, 0.25, 0.5, 0.75]
ALPHA = 0.5
MODEL_WEIGHT = 0.5  # share of the LightGBM prediction in the blend with nearest cells
NEIGHBOURS = prevalence.NEIGHBOURS
TOP = 3


def fit(x, y, weights):
    return {label: lgb.LGBMRegressor(**PARAMS).fit(x, y[:, i], sample_weight=weights)
            for i, label in enumerate(LABELS)}


def predict(models, x):
    p = np.column_stack([np.clip(models[label].predict(x), 0, None) for label in LABELS])
    return p / p.sum(1, keepdims=True).clip(1e-9)


def ecocrop_scores(cells):
    """ECOCROP suitability per label for each cell, using the cell's WorldClim normals (no soil)."""
    members = {label: [c for c in suitability.CROPS if prevalence.CROP_TO_LABEL.get(c["key"]) == label]
               for label in LABELS}
    out = np.zeros((len(cells), len(LABELS)))
    prec_cols = [f"prec_{m:02d}" for m in range(1, 13)]
    tavg_cols = [f"tavg_{m:02d}" for m in range(1, 13)]
    for row_i, row in enumerate(cells.itertuples(index=False)):
        r = row._asdict()
        prec, tavg = [r[c] for c in prec_cols], [r[c] for c in tavg_cols]
        rainy = [p >= 50 for p in prec]
        climate = {
            "monthly_rainfall": prec, "rain_by_year": [prec], "annual_rainfall_mm": round(sum(prec)),
            "monthly_temperature": tavg, "monthly_min_temperature": [t - 6 for t in tavg],
            "elevation_m": r["elevation"],
            "rainy_seasons": ["All year"] if all(rainy) else (["x"] if any(rainy) else []),
        }
        for j, label in enumerate(LABELS):
            out[row_i, j] = max(suitability.score_crop(c, climate, {})["score"] for c in members[label])
    return out


def combine(suit, shares, alpha):
    relative = shares / shares.max(1, keepdims=True).clip(1e-9)
    return suit * (alpha + (1 - alpha) * relative)


def evaluate(scores, truth, weights):
    """
    top3_overlap: how many of the 3 crops ranked highest are among the 3 most grown (0-1).
    share_covered: farmland share of the 3 ranked crops, relative to the best possible 3.
    Both are averaged over cells weighted by farmland area.
    """
    pred_top = np.argsort(-scores, 1)[:, :TOP]
    true_top = np.argsort(-truth, 1)[:, :TOP]
    overlap = np.array([len(set(p) & set(t)) / TOP for p, t in zip(pred_top, true_top)])
    covered = np.take_along_axis(truth, pred_top, 1).sum(1) / np.take_along_axis(truth, true_top, 1).sum(1).clip(1e-9)
    return {"top3_overlap": round(float(np.average(overlap, weights=weights)), 3),
            "share_covered": round(float(np.average(covered, weights=weights)), 3)}


def main():
    cells = pd.read_csv(HERE / "data" / "cells.csv")
    x = cells[prevalence.FEATURE_NAMES].to_numpy()
    y = cells[[f"share_{l}" for l in LABELS]].to_numpy()
    weights = np.sqrt(cells.farmland_ha.to_numpy())  # big farming areas count more, without swamping
    blocks = (np.floor(cells.lat) * 100 + np.floor(cells.lon)).astype(int)
    print(f"{len(cells)} cells in {blocks.nunique()} blocks; scoring ECOCROP for every cell ...", flush=True)
    suit = ecocrop_scores(cells)

    oof_model = np.zeros_like(y)
    oof_knn = np.zeros_like(y)
    oof_national = np.zeros_like(y)
    for fold, (tr, te) in enumerate(GroupKFold(n_splits=5).split(x, y, blocks)):
        oof_model[te] = predict(fit(x[tr], y[tr], weights[tr]), x[te])
        knn = KNeighborsRegressor(n_neighbors=NEIGHBOURS, weights="distance").fit(cells[["lat", "lon"]].to_numpy()[tr], y[tr])
        oof_knn[te] = knn.predict(cells[["lat", "lon"]].to_numpy()[te])
        oof_national[te] = np.average(y[tr], axis=0, weights=weights[tr])
        print(f"  fold {fold + 1}/5 done", flush=True)

    results = {
        "national average": evaluate(oof_national, y, weights),
        "nearest cells (map lookup)": evaluate(oof_knn, y, weights),
        "LightGBM model": evaluate(oof_model, y, weights),
        "model + nearest cells (used)": evaluate(oof_blend := MODEL_WEIGHT * oof_model + (1 - MODEL_WEIGHT) * oof_knn, y, weights),
        "ECOCROP only": evaluate(suit, y, weights),
    }
    for alpha in ALPHAS:
        results[f"ECOCROP x blend, alpha={alpha}"] = evaluate(combine(suit, oof_blend, alpha), y, weights)
    print("\nHeld-out areas (spatial cross-validation):")
    for name, r in results.items():
        print(f"  {name:32s} top-3 overlap {r['top3_overlap']:.2f}   farmland share covered {r['share_covered']:.2f}")

    per_label = {}
    for i, label in enumerate(LABELS):
        err = np.average(np.abs(oof_model[:, i] - y[:, i]), weights=weights)
        per_label[label] = {"mean_share": round(float(np.average(y[:, i], weights=weights)), 4),
                            "mean_abs_error": round(float(err), 4)}

    final = fit(x, y, weights)
    run = HERE / "runs" / datetime.now().strftime("%Y%m%d-%H%M%S")
    run.mkdir(parents=True)
    for label, model in final.items():
        model.booster_.save_model(str(run / f"{label}.txt"))
    config = {
        "labels": LABELS,
        "feature_names": prevalence.FEATURE_NAMES,
        "alpha": ALPHA,
        "model_weight": MODEL_WEIGHT,
        "neighbours": NEIGHBOURS,
        "data": "MapSPAM 2010 v2.0 harvested area (IFPRI, CC BY 4.0); WorldClim 2.1 normals (CC BY 4.0)",
        "trained_at": datetime.now().isoformat(timespec="seconds"),
        "cells": len(cells),
    }
    (run / "model_config.json").write_text(json.dumps(config, indent=2))
    (run / "metrics.json").write_text(json.dumps({"spatial_cv": results, "per_label": per_label}, indent=2))

    target = prevalence.MODEL_DIR
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(run, target)
    print(f"saved to {run} and installed in {target}")


if __name__ == "__main__":
    main()
