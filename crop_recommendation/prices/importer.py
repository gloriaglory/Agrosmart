"""
Download and load the WFP food prices dataset for Tanzania.

Source: World Food Programme, published on the Humanitarian Data Exchange
(https://data.humdata.org/dataset/wfp-food-prices-for-united-republic-of-tanzania),
licence CC BY-IGO. Prices are collected mainly by Tanzania's Ministry of
Industry and Trade and are updated monthly.
"""
import csv
import io
from datetime import date

import httpx
from django.db import transaction

from .models import MarketPrice, PriceImport

HDX_DATASET_API = (
    "https://data.humdata.org/api/3/action/package_show"
    "?id=wfp-food-prices-for-united-republic-of-tanzania"
)

# Convert units to kilograms; other units (e.g. litres of oil) are skipped
UNIT_TO_KG = {"KG": 1, "100 KG": 100, "MT": 1000, "50 KG": 50, "90 KG": 90}

# WFP region names that differ from the names used elsewhere in AgroSmart
REGION_NAMES = {"Dar-es-salaam": "Dar es Salaam", "Dar es salaam": "Dar es Salaam"}


def latest_csv_url():
    """Find the current download link for the food prices CSV on HDX."""
    response = httpx.get(HDX_DATASET_API, timeout=30.0)
    response.raise_for_status()
    resources = response.json()["result"]["resources"]
    for resource in resources:
        if "food prices" in resource.get("name", "").lower() and resource["url"].endswith(".csv"):
            return resource["url"]
    return resources[0]["url"]


def download_csv(url):
    response = httpx.get(url, timeout=120.0, follow_redirects=True)
    response.raise_for_status()
    return response.text


def parse_rows(text):
    """Yield MarketPrice objects (unsaved) from the CSV text, skipping unusable rows."""
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        if row.get("date", "").startswith("#"):  # HDX tag row under the header
            continue
        kg = UNIT_TO_KG.get((row.get("unit") or "").strip().upper())
        if not kg or row.get("currency") != "TZS":
            continue
        try:
            year, month, _day = (int(x) for x in row["date"].split("-"))
            price = float(row["price"])
        except (KeyError, ValueError):
            continue
        if price <= 0:
            continue
        try:
            lat, lon = float(row["latitude"]), float(row["longitude"])
        except (KeyError, ValueError):
            lat = lon = None
        region = (row.get("admin1") or "").strip()
        yield MarketPrice(
            date=date(year, month, 1),
            region=REGION_NAMES.get(region, region),
            district=(row.get("admin2") or "").strip(),
            market=row["market"].strip(),
            latitude=lat,
            longitude=lon,
            category=(row.get("category") or "").strip(),
            commodity=row["commodity"].strip(),
            price_type=row["pricetype"].strip().lower(),
            unit=row["unit"].strip().upper(),
            price=round(price, 2),
            price_per_kg=price / kg,
        )


@transaction.atomic
def load_prices(text, source_url=""):
    """Insert or update prices from CSV text. Returns the PriceImport record."""
    objects = list(parse_rows(text))
    # Later rows win if the file repeats a key
    unique = {(o.date, o.market, o.commodity, o.price_type, o.unit): o for o in objects}
    objects = list(unique.values())
    MarketPrice.objects.bulk_create(
        objects,
        batch_size=2000,
        update_conflicts=True,
        unique_fields=["date", "market", "commodity", "price_type", "unit"],
        update_fields=["price", "price_per_kg", "region", "district", "latitude", "longitude", "category"],
    )
    latest = max((o.date for o in objects), default=None)
    return PriceImport.objects.create(
        source_url=source_url,
        rows_read=text.count("\n"),
        rows_saved=len(objects),
        latest_date=latest,
    )
