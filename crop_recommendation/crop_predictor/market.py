"""
Market context for a recommended crop: today's price (WFP market data, prices app), the
usual best month to sell, and the typical local yield (MapSPAM), giving a rough income
per hectare. Shown alongside recommendations, not used to rank them: prices only cover
a few crops and costs differ widely between crops.
"""
from prices.analysis import commodity_detail

from .climate import MONTHS
from .prevalence import typical_yield

# Recommended crops -> WFP commodities that still have current prices
PRICE_COMMODITY = {
    "maize": "Maize",
    "rice": "Rice",
    "beans": "Beans",
    "irish_potato": "Potatoes (Irish)",
    "sorghum": "Sorghum",
    "finger_millet": "Millet (finger)",
    "pearl_millet": "Millet (bulrush)",
    "wheat": "Wheat",
}
# MapSPAM yields are for the harvested crop; WFP prices rice after milling (~65% of paddy weight)
SOLD_FRACTION = {"rice": 0.65}


def _price(commodity, region):
    """Regional price detail if WFP covers the region, otherwise national."""
    try:
        detail = commodity_detail(commodity, region) if region else None
        if not detail or "error" in detail:
            detail = commodity_detail(commodity)
    except Exception as e:
        print(f"Price lookup failed for {commodity}: {e}")
        return None
    return None if not detail or "error" in detail else detail


def market_info(crop_key, region, lat, lon):
    """Price, best selling month, local yield and income per hectare, with a one-line summary."""
    info = {"price_tzs_per_kg": None, "price_month": None, "price_area": None,
            "best_month_to_sell": None, "yield_kg_per_ha": None, "income_tzs_per_ha": None}
    parts = []

    commodity = PRICE_COMMODITY.get(crop_key)
    detail = _price(commodity, region) if commodity else None
    if detail and detail["current"]["price"]:
        info.update(price_tzs_per_kg=detail["current"]["price"], price_month=detail["current"]["date"],
                    price_area=detail["region"])
        parts.append(f"Market price about TZS {detail['current']['price']:,}/kg in {detail['region']} "
                     f"({detail['current']['date']}); farm-gate prices are lower.")
        season = detail.get("seasonality")
        if season and season["spread_pct"] >= 10:
            info["best_month_to_sell"] = MONTHS[season["best_month"] - 1]
            parts.append(f"Prices are usually highest in {info['best_month_to_sell']}.")

    kg = typical_yield(lat, lon, crop_key)
    if kg:
        info["yield_kg_per_ha"] = round(kg)
        if info["price_tzs_per_kg"]:
            income = kg * SOLD_FRACTION.get(crop_key, 1.0) * info["price_tzs_per_kg"]
            info["income_tzs_per_ha"] = round(income, -3)
            parts.append(f"Farms around here typically harvest {kg / 1000:.1f} t/ha, worth up to about "
                         f"TZS {income / 1e6:.1f} million per hectare at market prices, before costs.")
        else:
            parts.append(f"Farms around here typically harvest {kg / 1000:.1f} t/ha.")

    info["summary"] = " ".join(parts) or None
    return info
