# Crop recommendation: "what is grown here" model

Trains the model that weights crop suitability (FAO ECOCROP, `crop_predictor/suitability.py`)
by what farmers around a location actually grow.

```bash
cd ml/crop
./download_data.sh                                   # ~550 MB: MapSPAM 2010 + WorldClim 2.1
../../crop_recommendation/venv/bin/pip install -r requirements.txt
../../crop_recommendation/venv/bin/python prepare_data.py
../../crop_recommendation/venv/bin/python train.py   # ~3 min; installs into crop_predictor/ml_models/prevalence/
```

## Data
- **Labels:** MapSPAM 2010 v2.0 (IFPRI, CC BY 4.0). These are the harvested area of each crop in about 6,800 Tanzanian 10 km cells, turned into each crop's share of farmland.
  - MapSPAM's "rest of crops" stands in for cashew. In Tanzania it sits almost entirely in the cashew belt and adds up to about the national cashew area.
  - Some crops are only recorded as groups, so they share a label: other pulses, vegetables and tropical fruit.
- **Features:** WorldClim 2.1 normals (CC BY 4.0), giving monthly rainfall and temperature, elevation, derived season measures, and latitude and longitude. The clipped grid ships with the app (`crop_predictor/data/worldclim_tz.npz`), so training and live use read the same inputs.
- **Newer data:** MapSPAM 2020 needs a short guestbook form on Harvard Dataverse (doi:10.7910/DVN/SWPENT). With its CSVs in `data/raw`, `prepare_data.py` needs only the file names and column suffixes changed.

## Model and results
- One LightGBM regressor per crop predicts its share of farmland, averaged with the shares in the 8 nearest cells.
- It was tested with spatial cross-validation: whole 1°×1° blocks held out, on cells it never saw.

| Method | Top-3 overlap with crops actually grown | Farmland share covered |
|---|---|---|
| National average | 0.44 | 0.60 |
| Nearest cells only | 0.71 | 0.85 |
| LightGBM only | 0.68 | 0.85 |
| **LightGBM + nearest cells (used)** | **0.72** | **0.87** |
| ECOCROP suitability only | 0.29 | 0.40 |
| ECOCROP × local farming, α=0.5 (app) | 0.64 | 0.81 |

The app ranks crops by `suitability × (α + (1 − α) × local share / largest local share)` with α=0.5.
α=0 matches current farming best, but it would never suggest a suitable crop that is new to an
area. α=0.5 is a deliberate balance, not a tuned value.
