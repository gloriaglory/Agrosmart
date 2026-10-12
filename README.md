<p align="center">
  <img src="Web/src/assets/images/logo-mark.png" alt="AgroSmart logo" height="96" />
</p>

<h1 align="center">AgroSmart</h1>

<p align="center">
  Smart farming tools for Tanzania: crop recommendations, leaf disease detection,
  market prices, a verified-seller marketplace and farming education in one place.
</p>

---

## Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
  - [Demo data](#demo-data)
- [Configuration](#configuration)
- [API overview](#api-overview)
- [How key parts work](#how-key-parts-work)
  - [Market prices and outlook](#market-prices-and-outlook)
- [Testing](#testing)
- [Running with Docker](#running-with-docker)
- [Known limitations](#known-limitations)

## Features

| Area | What it does |
|---|---|
| **Crop recommendation** | Pick a region or click a map. Each of 36 Tanzanian crops' needs (FAO ECOCROP) is scored against the spot's soil (iSDA), altitude and long-term climate (Open-Meteo), then weighted by what farmers nearby grow (a LightGBM model trained on MapSPAM). Gives the top 3 crops with planting month, reasons, market price and typical income, a 5-day planting forecast (OpenWeatherMap) and soil fertility advice. |
| **Disease detection** | Upload a leaf photo; a TensorFlow/Keras model recognises 74 conditions across 19 crops (including maize, tomato, potato, rice, cotton, sugarcane, citrus and wheat) and gives treatment and prevention advice. |
| **Marketplace** | Sellers list produce with a region and town. Buyers search and filter by region and contact sellers directly. |
| **Verified sellers** | Selling requires a valid 20-digit NIDA number, full name and phone. Numbers are checked, unique and locked once saved. Ready for NIDA API integration. |
| **Market prices** | Real monthly prices from 63 markets (WFP), with a 3-month price outlook range, the best month to sell and prices by region, in the Marketplace's "Price trends" tab. |
| **Market insights** | The home page shows current crop prices, listings per crop and a map of what is for sale in each region. |
| **Education** | Articles and YouTube videos with Instagram-style comments: likes, replies and `@username` tagging. |
| **Content moderation** | Posts and comments pass a blocked-words filter (English and Kiswahili) and AI safety checks for text and images. |
| **Farming assistant** | A chatbot that answers farming questions in Kiswahili or English. |
| **Accounts** | Username/password login, with Google and Facebook sign-in ready once keys are added. |

## Tech stack

**Backend** (`crop_recommendation/`)
- Python 3.11, Django 5.2, Django REST Framework, token authentication
- django-allauth and dj-rest-auth for social login
- Machine learning: LightGBM and scikit-learn (crop model), TensorFlow 2.19 and Keras 3.13 (disease model)
- External services: iSDA soil API, OpenWeatherMap, Open-Meteo, Google Geocoding, Groq (LLM chat and safety models), YouTube oEmbed
- SQLite by default, PostgreSQL optional

**Frontend** (`Web/`)
- React 19, TypeScript, Vite 6
- Tailwind CSS 3
- Leaflet with OpenStreetMap, Recharts, Axios, React Router 7

## Project structure

```
Agrosmart/
├── crop_recommendation/          Django backend
│   ├── crop_recommendation/      Project settings and URLs
│   ├── authentication/           Users, NIDA checks, social login, user search
│   ├── market_place/             Listings, regions, seller permissions
│   ├── crop_predictor/           Crop recommendation model and data sources
│   ├── disease_detection/        Leaf disease model (Keras, stored with Git LFS)
│   ├── education/                Posts, comments, mentions, moderation
│   ├── bot/                      Farming assistant (Groq)
│   ├── requirements.txt
│   ├── .env.example              Copy to .env and fill in
│   └── manage.py
└── Web/                          React frontend
    ├── src/
    │   ├── pages/                One file per page
    │   ├── components/           Navbar, footer, maps, comments, etc.
    │   ├── assets/               Images, logo, hero video
    │   └── config.ts             Backend address (from .env)
    ├── .env.example
    └── package.json
```

## Getting started

### Prerequisites

- **Python 3.11.** TensorFlow 2.19 does not support Python 3.13 or 3.14 yet.
- **Node.js 20+** and npm
- **Git LFS**, to download the disease detection models
- **macOS only:** `libomp`, needed by LightGBM

```bash
# macOS (Homebrew)
brew install git-lfs libomp
git lfs install
```

### 1. Clone and fetch the models

```bash
git clone https://github.com/gloriaglory/Agrosmart.git
cd Agrosmart
git lfs pull        # downloads the disease model, crop model and landing video (~240 MB)
```

### 2. Backend

```bash
cd crop_recommendation
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env              # then fill in the values (see Configuration)
python manage.py migrate
python manage.py seed_demo        # optional, sample accounts, listings and posts
python manage.py refresh_prices   # download real market prices (about 65,000 rows, ~10 s)
python manage.py createsuperuser  # optional, for the admin at /admin
python manage.py runserver        # http://localhost:8765
```

#### Demo data

`seed_demo` fills a fresh database so every page has something to show:
18 marketplace listings across 13 regions, education posts with comments, and these accounts:

| Username | Role |
|---|---|
| `demo_buyer` | Buyer |
| `asha_farms` | Seller, NIDA verified |
| `baraka_mkulima` | Seller, not yet verified |

All demo accounts use the password `AgroSmart-demo-2026` (change it with `--password`).
The NIDA numbers are fake. Running the command again resets the demo data and leaves other data untouched.

### 3. Frontend

In a second terminal:

```bash
cd Web
cp .env.example .env              # points the app at http://localhost:8765
npm install
npm run dev                       # http://localhost:5173
```

## Configuration

### Backend: `crop_recommendation/.env`

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | | `True` for development. Defaults to `False`. |
| `PORT` | | Port for `runserver`. Defaults to `8765`. |
| `GOOGLE_API_KEY` | For recommendations | Google Geocoding (address to coordinates) |
| `OPENWEATHER_API_KEY` | For recommendations | 5-day forecast for planting advice |
| `ISDA_API_KEY` | For recommendations | Soil properties for Africa |
| `GROQ_API_KEY` | For chatbot and moderation | From [console.groq.com](https://console.groq.com) |
| `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET` | For Google login | Google Cloud Console, OAuth client (Web application) |
| `FACEBOOK_APP_ID` / `_SECRET` | For Facebook login | Facebook for Developers app settings |
| `REQUIRE_NIDA_VERIFICATION` | | `True` to let only NIDA-verified sellers post listings |
| `USE_POSTGRES`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | | Use PostgreSQL instead of SQLite |
| `CHAT_MODEL`, `MODERATION_MODEL`, `MODERATION_FALLBACK_MODEL`, `IMAGE_MODERATION_MODEL` | | Override the Groq models if one is retired |

Features whose keys are missing switch off gracefully: social login buttons are hidden, and posts wait for admin review instead of AI checks.

### Frontend: `Web/.env`

| Variable | Description |
|---|---|
| `VITE_API_URL` | Backend address, e.g. `http://localhost:8765` |

> `.env` files are git-ignored. Never commit real keys.

## API overview

All endpoints return JSON. Send `Authorization: Token <token>` for endpoints that need login.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Sign up as a buyer or seller (`account_type`, `id_number` for sellers) |
| POST | `/api/auth/login/` | Log in; returns `{ user, token }` |
| GET | `/api/auth/profile/` | Current user |
| PATCH | `/api/auth/profile/update/` | Update name, phone, NIDA number |
| POST | `/api/auth/nida/verify/` | Request NIDA verification |
| GET | `/api/auth/users/search/?q=` | Find accounts to `@tag` (login required) |
| POST | `/api/auth/google/`, `/api/auth/facebook/` | Exchange a provider access token for a login |
| GET, POST | `/market/items/` | List (`?region=`, `?search=`) or create listings (sellers) |
| GET, PATCH, DELETE | `/market/items/<id>/` | View, edit or delete a listing (owner only) |
| GET | `/market/items/mine/` | The current seller's listings |
| GET | `/market/items/regions/` | Crops for sale per region, for the map |
| POST | `/api/recommend/` | Top 3 crops for `{ latitude, longitude }`, with climate summary and soil notes |
| POST | `/detector/detect` | Disease detection (multipart `image`) |
| GET, POST | `/api/education/contents/` | List or create posts |
| GET, POST | `/api/education/comments/?content=<id>` | List or add comments |
| POST | `/api/education/comments/<id>/like/` | Like or unlike a comment |
| GET | `/api/prices/` | Crops with current market prices |
| GET | `/api/prices/detail/?commodity=&region=` | Price history, 3-month outlook range, seasonality, prices by region |
| POST | `/api/bot/ask/` | Ask the farming assistant `{ question }` |

## How key parts work

### NIDA seller verification
- A NIDA number has 20 digits (`YYYYMMDD-XXXXX-XXXXX-XX`). The first 8 digits are the holder's date of birth.
- On sign-up and profile updates, numbers must have a real past birth date and the holder must be at least 18. Each number can only be registered once.
- A valid number cannot be changed once saved. Changing your first or last name removes verified status.
- To connect the real NIDA service, implement `verify_nida()` in `crop_recommendation/authentication/nida.py`. Until then, admins can verify sellers in the Django admin ("Mark NIDA as verified").

### Content moderation
1. **Blocked words:** `crop_recommendation/education/moderation/blocked_words.txt`, one word or phrase per line. Matching is whole-word, so "shiitake" is not caught by "shit".
2. **AI checks via Groq:** text is classified against an AgroSmart policy that allows normal farming language, such as killing pests or slaughtering livestock. Thumbnails are checked by a vision model.
3. If the AI check cannot run (no key, or rate-limited), posts wait as **Pending review**. Admins approve them in **Django admin → Contents**. Comments are only blocked when clearly unsafe.

### Market prices and outlook
- **Data:** the [WFP food prices dataset for Tanzania](https://data.humdata.org/dataset/wfp-food-prices-for-united-republic-of-tanzania) (CC BY-IGO), collected mainly by the Ministry of Industry and Trade. It has monthly prices from 63 markets in 25 regions since 2006.
- **Refreshing:** `python manage.py refresh_prices` downloads the latest file and updates prices in place. Run it monthly, for example with cron: `0 6 5 * * cd /path/to/crop_recommendation && venv/bin/python manage.py refresh_prices`. Use `--file prices.csv` to load a downloaded file instead.
- **Units:** all prices are converted to TZS per kg. Wholesale prices are used where they are current, retail otherwise. Crops that WFP stopped tracking more than 12 months ago are hidden.
- **Outlook:** single-number price predictions were tested and did not beat "next month = this month", so the app shows an honest **range**. For each of the next 3 months, it uses the middle 80% of price moves from the same time of year over the last 10 years. Each crop shows its measured hit rate: on the past 12 months, real prices fell inside the range 79–93% of the time for the main crops.
- **Seasonality:** the typical price in each month relative to the yearly average over 15 years, giving the best month to sell and the cheapest month.
- **API:** `GET /api/prices/` (crops and current prices) and `GET /api/prices/detail/?commodity=Maize&region=Dodoma`.

### Crop recommendation
Suitability scoring with the FAO ECOCROP method (`crop_predictor/suitability.py`):

- **Crop needs:** ideal and absolute ranges for temperature, yearly rainfall and soil pH, plus preferred soil texture and depth and the highest altitude, for 36 Tanzanian crops. These come from FAO ECOCROP, with a few documented local corrections (highland banana, sorghum, arabica, tea, cashew's dry season). `python crop_predictor/data/build_crops.py` rebuilds `crop_predictor/data/crops.json`.
- **Location data:**
  - iSDA soil layers: pH, N, P, K, organic carbon, texture, depth to bedrock, slope and land cover.
  - Open-Meteo history: 10 years of rainfall and 3 years of temperature, adjusted for altitude.
  - Results are cached for 30 days.
- **Scoring:**
  - Each factor scores 0–1 and the weakest one sets the crop's score.
  - Rainfall is scored year by year, so unreliable rain counts against a crop.
  - Seasonal crops get the planting month whose season fits best, starting in a rainy month.
- **Local farming:** a LightGBM model trained on MapSPAM predicts each crop's share of local farmland. It is averaged with the nearest MapSPAM cells and multiplies suitability by `0.5 + 0.5 × share / largest share`, so proven local crops rise but suitable new ones still appear. Training, data and spatial cross-validation results are in [`ml/crop/README.md`](ml/crop/README.md).
- **Market** (`market.py`): the current market price and usual best month to sell from the prices app, and the typical local yield from MapSPAM, giving a rough income per hectare. It is shown, not used for ranking.
- **Planting forecast** (`forecast.py`): the OpenWeatherMap 5-day forecast is checked against the common start-of-rains rule (about 20 mm within 3 days) and the crops' planting months.
- **Output:** the top 3 crops with match score, planting month, main limiting factor and a plain-English explanation, plus soil advice (low N, P, K or organic matter, acidity, steep slopes) and warnings for non-farmland.
- The Kaggle-style classifier in `crop_predictor/ml_models/crop/` (`services.py`) still loads for comparison but is not used. Its training data is not Tanzanian and its units do not match iSDA. For example, iSDA potassium values make it predict apple or grapes almost everywhere.

## Testing

```bash
cd crop_recommendation
source venv/bin/activate
python manage.py test
```

The suite covers authentication and NIDA rules, marketplace permissions, education comments and moderation, the chatbot and recommendations. Tests never call external services: Groq, YouTube, iSDA and the weather APIs are simulated, and uploads go to a temporary folder.

Frontend checks:

```bash
cd Web
npx tsc -b && npm run lint && npm run build
```

## Running with Docker

```bash
cd crop_recommendation
docker compose up --build    # http://localhost:8765
docker compose exec server python manage.py createsuperuser
```

## Known limitations

- **NIDA verification** is not yet connected to the NIDA service. Verification is manual through the admin.
- **Groq free tier:** the moderation model allows only a few requests per minute. A fallback model is used automatically, and posts go to review if both are busy.
- **Social login** needs Google and Facebook app credentials. Facebook login on a live site requires HTTPS and Facebook app review.
- **Hero video** (`Web/src/assets/videos/`) is about 44 MB. Compress it before deploying to production.
