"""
What farmers around a location actually grow, learned from MapSPAM.

A LightGBM model per crop (ml/crop/train.py) predicts each crop's share of the farmland
in a ~10 km square from its long-term climate and position, and is averaged with the
shares in the nearest MapSPAM cells; in tests on held-out areas the average beat both.
Training and the live app read the same inputs: WorldClim normals clipped to Tanzania
(data/worldclim_tz.npz) and MapSPAM cells (data/spam_tz.npz).

This module has no Django dependency so the training scripts can import it.
"""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
WORLDCLIM_PATH = HERE / "data" / "worldclim_tz.npz"
SPAM_PATH = HERE / "data" / "spam_tz.npz"
MODEL_DIR = HERE / "ml_models" / "prevalence"

SPAM_CELL_DEG = 5 / 60  # MapSPAM grid: 5 arc-minutes
NEIGHBOURS = 8

# Model labels -> MapSPAM 2010 crop codes. Some SPAM codes cover several crops.
LABELS = {
    "maize": ["maiz"], "rice": ["rice"], "sorghum": ["sorg"], "pearl_millet": ["pmil"],
    "finger_millet": ["smil"], "wheat": ["whea"], "cassava": ["cass"], "sweet_potato": ["swpo"],
    "irish_potato": ["pota"], "beans": ["bean"], "cowpea": ["cowp"], "pigeon_pea": ["pige"],
    "chickpea": ["chic"], "groundnut": ["grou"], "soybean": ["soyb"], "sunflower": ["sunf"],
    "sesame": ["sesa"], "cotton": ["cott"], "tobacco": ["toba"], "coffee_arabica": ["acof"],
    "coffee_robusta": ["rcof"], "tea": ["teas"], "sugarcane": ["sugc"], "banana": ["bana", "plnt"],
    "other_pulses": ["opul"], "vegetables": ["vege"], "tropical_fruit": ["trof"],
    # MapSPAM has no cashew code; in Tanzania its "rest of crops" is almost all in the cashew
    # belt (Mtwara, Lindi, Pwani, Ruvuma) and totals ~380,000 ha, about the national cashew area.
    "cashew": ["rest"],
}
# Recommended crops that MapSPAM only records as part of a group
CROP_TO_LABEL = {key: key for key in LABELS} | {
    "green_gram": "other_pulses", "bambara_nut": "other_pulses", "peas": "other_pulses",
    "tomato": "vegetables", "onion": "vegetables", "cabbage": "vegetables", "watermelon": "vegetables",
    "avocado": "tropical_fruit", "mango": "tropical_fruit", "orange": "tropical_fruit",
    "pineapple": "tropical_fruit",
}


# ---------------------------------------------------------------- climate inputs

@lru_cache(maxsize=1)
def _worldclim():
    data = np.load(WORLDCLIM_PATH)
    return {k: data[k] for k in data.files}


def worldclim_at(lat, lon):
    """
    Monthly rainfall (mm), monthly mean temperature (°C) and elevation (m), averaged over
    the MapSPAM cell containing the point, or None outside the clipped area.
    """
    wc = _worldclim()
    west, north, res = float(wc["west"]), float(wc["north"]), float(wc["res"])
    # Snap to the SPAM 5' cell, then average the WorldClim 2.5' pixels inside it
    cell_west = np.floor(lon / SPAM_CELL_DEG) * SPAM_CELL_DEG
    cell_north = np.ceil(lat / SPAM_CELL_DEG) * SPAM_CELL_DEG
    c0 = int(round((cell_west - west) / res))
    r0 = int(round((north - cell_north) / res))
    step = int(round(SPAM_CELL_DEG / res))
    rows, cols = slice(r0, r0 + step), slice(c0, c0 + step)
    if r0 < 0 or c0 < 0 or r0 + step > wc["elev"].shape[0] or c0 + step > wc["elev"].shape[1]:
        return None
    elev = wc["elev"][rows, cols].astype(float)
    if (elev == wc["nodata"]).all():
        return None  # sea or lake
    valid = elev != wc["nodata"]
    prec = [float(wc["prec"][m][rows, cols][valid].mean()) for m in range(12)]
    tavg = [float(wc["tavg"][m][rows, cols][valid].mean()) / 10 for m in range(12)]
    return prec, tavg, float(elev[valid].mean())


def features(prec, tavg, elev, lat, lon):
    """Model inputs for one place (same order as FEATURE_NAMES)."""
    prec, tavg = np.asarray(prec, float), np.asarray(tavg, float)
    annual = prec.sum()
    quarters = [prec[[m, (m + 1) % 12, (m + 2) % 12]].sum() for m in range(12)]
    wettest = int(np.argmax(quarters))
    rainy = prec >= 50
    seasons = sum(1 for m in range(12) if rainy[m] and not rainy[m - 1]) if not rainy.all() else 1
    angle = 2 * np.pi * (wettest + 1) / 12  # wettest quarter's middle month, on a circle
    return [
        *prec, *tavg,
        annual, prec.max(), prec.min(), prec.std() / (prec.mean() or 1),
        max(quarters), min(quarters), np.sin(angle), np.cos(angle),
        int(rainy.sum()), int((prec >= 100).sum()), seasons,
        tavg.mean(), tavg.min(), tavg.max(), tavg.max() - tavg.min(),
        elev, lat, lon,
    ]


FEATURE_NAMES = (
    [f"prec_{m:02d}" for m in range(1, 13)] + [f"tavg_{m:02d}" for m in range(1, 13)] + [
        "prec_annual", "prec_wettest_month", "prec_driest_month", "prec_seasonality",
        "prec_wettest_quarter", "prec_driest_quarter", "wet_quarter_sin", "wet_quarter_cos",
        "months_over_50mm", "months_over_100mm", "rainy_seasons",
        "tavg_mean", "tavg_coldest_month", "tavg_warmest_month", "tavg_range",
        "elevation", "lat", "lon",
    ]
)


# ---------------------------------------------------------------- model

@lru_cache(maxsize=1)
def _model():
    """The trained boosters, or None if the model has not been installed."""
    config_path = MODEL_DIR / "model_config.json"
    if not config_path.exists():
        return None
    import lightgbm as lgb
    config = json.loads(config_path.read_text())
    boosters = {label: lgb.Booster(model_file=str(MODEL_DIR / f"{label}.txt")) for label in config["labels"]}
    return config, boosters


def nearest_shares(lat, lon, k=NEIGHBOURS):
    """Crop shares in the k nearest MapSPAM cells, weighted by closeness (as in training)."""
    data = _spam()
    distance = np.hypot(data["lat"] - lat, data["lon"] - lon)
    nearest = np.argsort(distance)[:k]
    weights = 1 / np.maximum(distance[nearest], 1e-9)
    return np.average(data["shares"][nearest], axis=0, weights=weights)


def local_shares(lat, lon):
    """Expected share of local farmland for each label (summing to 1), or None."""
    model = _model()
    climate = worldclim_at(lat, lon) if WORLDCLIM_PATH.exists() else None
    if model is None or climate is None or _spam() is None:
        return None
    config, boosters = model
    x = np.array([features(*climate, lat, lon)])
    predicted = np.array([max(float(boosters[label].predict(x)[0]), 0.0) for label in config["labels"]])
    predicted /= predicted.sum() or 1.0
    labels = list(_spam()["labels"])
    nearby = nearest_shares(lat, lon)[[labels.index(label) for label in config["labels"]]]
    nearby /= nearby.sum() or 1.0
    blend = config.get("model_weight", 0.5)
    return dict(zip(config["labels"], blend * predicted + (1 - blend) * nearby))


def ecocrop_weight():
    """How much a crop's suitability counts on its own, versus being grown locally (train.py)."""
    model = _model()
    return model[0]["alpha"] if model else 1.0


# ---------------------------------------------------------------- yields

@lru_cache(maxsize=1)
def _spam():
    if not SPAM_PATH.exists():
        return None
    data = np.load(SPAM_PATH)
    return {k: data[k] for k in data.files}


def typical_yield(lat, lon, crop_key, radius_km=25):
    """
    MapSPAM 2010 rain-fed yield (kg/ha) around a point: the area-weighted average over nearby
    cells where the crop is grown, or None. Only crops MapSPAM records individually.
    """
    data = _spam()
    label = CROP_TO_LABEL.get(crop_key)
    if data is None or label != crop_key or label not in list(data["labels"]):
        return None
    i = list(data["labels"]).index(label)
    dy = (data["lat"] - lat) * 111.0
    dx = (data["lon"] - lon) * 111.0 * np.cos(np.radians(lat))
    near = (dx ** 2 + dy ** 2 <= radius_km ** 2) & (data["area"][:, i] > 0) & (data["yield"][:, i] > 0)
    if not near.any():
        return None
    return float(np.average(data["yield"][near, i], weights=data["area"][near, i]))
