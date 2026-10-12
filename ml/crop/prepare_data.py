"""
Step 1: build the training table for the "what is grown here" model.

    ./download_data.sh
    python prepare_data.py

Writes:
  data/cells.csv                                   one row per Tanzanian MapSPAM cell: features + crop shares
  crop_predictor/data/worldclim_tz.npz             WorldClim normals clipped to Tanzania (used live by the app)
  crop_predictor/data/spam_tz.npz                  crop shares and rain-fed yields per cell (used live by the app)
"""
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
APP = HERE.parents[1] / "crop_recommendation"
sys.path.insert(0, str(APP))
from crop_predictor import prevalence  # noqa: E402

# Tanzania with a margin, so cells on the border still have every neighbouring pixel
BOUNDS = dict(west=29.0, south=-12.5, east=41.0, north=-0.5)
MIN_FARMLAND_HA = 100  # skip cells with almost no crops (parks, lakes, towns)


def read_spam(zip_name, member, crops, suffix):
    """Tanzanian rows of a MapSPAM file, with one column per crop code."""
    columns = ["iso3", "cell5m", "x", "y"] + [f"{c}_{suffix}" for c in crops]
    with zipfile.ZipFile(RAW / zip_name) as z, z.open(member) as f:
        reader = pd.read_csv(f, usecols=columns, chunksize=200_000, encoding="latin-1")
        parts = [chunk[chunk.iso3 == "TZA"] for chunk in reader]
    table = pd.concat(parts).drop(columns="iso3").set_index("cell5m")
    return table.rename(columns={f"{c}_{suffix}": c for c in crops})


def clip_worldclim(variable):
    """12 monthly WorldClim 2.5' grids (or one for elevation) clipped to BOUNDS."""
    arrays, profile = [], None
    with zipfile.ZipFile(RAW / f"wc2.1_2.5m_{variable}.zip") as z:
        names = sorted(n for n in z.namelist() if n.endswith(".tif"))
        for name in names:
            with rasterio.open(f"/vsizip/{RAW / f'wc2.1_2.5m_{variable}.zip'}/{name}") as src:
                window = from_bounds(BOUNDS["west"], BOUNDS["south"], BOUNDS["east"], BOUNDS["north"],
                                     transform=src.transform).round_offsets().round_lengths()
                arrays.append(src.read(1, window=window))
                profile = (src.window_transform(window), src.nodata)
    return arrays, profile


def main():
    all_codes = sorted({c for codes in prevalence.LABELS.values() for c in codes})
    spam_codes = ["whea", "rice", "maiz", "barl", "pmil", "smil", "sorg", "ocer", "pota", "swpo", "yams",
                  "cass", "orts", "bean", "chic", "cowp", "pige", "lent", "opul", "soyb", "grou", "cnut",
                  "oilp", "sunf", "rape", "sesa", "ooil", "sugc", "sugb", "cott", "ofib", "acof", "rcof",
                  "coco", "teas", "toba", "bana", "plnt", "trof", "temf", "vege", "rest"]

    print("reading MapSPAM harvested area and yield for Tanzania ...", flush=True)
    area = read_spam("spam2010_harv_area.csv.zip", "spam2010V2r0_global_H_TA.csv", spam_codes, "a")
    yields = read_spam("spam2010_yield.csv.zip", "spam2010V2r0_global_Y_TR.csv", all_codes, "r")
    print(f"  {len(area)} cells")

    print("clipping WorldClim to Tanzania ...", flush=True)
    prec, (transform, _) = clip_worldclim("prec")
    tavg, _ = clip_worldclim("tavg")
    (elev,), _ = clip_worldclim("elev")
    # tavg is stored x10 as int16 to keep the file small; rainfall and elevation as int16
    wc_nodata = -32768
    prec, tavg = np.array(prec), np.array(tavg)
    np.savez_compressed(
        APP / "crop_predictor" / "data" / "worldclim_tz.npz",
        # WorldClim marks sea and lakes with a huge negative number (different per variable)
        prec=np.round(np.where(prec < -1000, 0, prec)).astype(np.int16),
        tavg=np.round(np.where(tavg < -1000, 0, tavg) * 10).astype(np.int16),
        elev=np.where(elev < -1000, wc_nodata, elev).astype(np.int16),
        nodata=wc_nodata, west=transform.c, north=transform.f, res=transform.a,
    )
    prevalence._worldclim.cache_clear()

    print("building features and crop shares ...", flush=True)
    total = area[spam_codes].sum(axis=1)
    area = area[total >= MIN_FARMLAND_HA]
    total = total[area.index]
    rows = []
    for cell, r in area.iterrows():
        climate = prevalence.worldclim_at(r.y, r.x)
        if climate is None:
            continue
        row = dict(zip(prevalence.FEATURE_NAMES, prevalence.features(*climate, r.y, r.x)))
        row.update(cell=cell, farmland_ha=total[cell])
        for label, codes in prevalence.LABELS.items():
            row[f"share_{label}"] = sum(r[c] for c in codes) / total[cell]
        rows.append(row)
    cells = pd.DataFrame(rows)
    cells.to_csv(HERE / "data" / "cells.csv", index=False)

    labels = list(prevalence.LABELS)
    keep = yields.index.intersection(area.index)
    label_area = np.stack([area.loc[keep, prevalence.LABELS[l]].sum(axis=1) for l in labels], 1)
    np.savez_compressed(
        APP / "crop_predictor" / "data" / "spam_tz.npz",
        labels=np.array(labels), lat=area.loc[keep, "y"].to_numpy(np.float32),
        lon=area.loc[keep, "x"].to_numpy(np.float32),
        area=label_area.astype(np.float32),
        shares=(label_area / total[keep].to_numpy()[:, None]).astype(np.float32),
        # For merged codes (banana + plantain) use the larger yield; both are bananas
        **{"yield": np.stack([yields.loc[keep, prevalence.LABELS[l]].max(axis=1) for l in labels], 1).astype(np.float32)},
    )

    shares = cells[[f"share_{l}" for l in labels]]
    print(f"\n{len(cells)} farmland cells. Average share of farmland (top 12):")
    print((shares.mean().sort_values(ascending=False).head(12) * 100).round(1).to_string())


if __name__ == "__main__":
    main()
