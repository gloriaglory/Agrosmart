"""
Crop suitability scoring, following the FAO ECOCROP method (Hijmans et al., dismo::ecocrop).

Each crop has an absolute and an ideal range for temperature, yearly rainfall and soil pH,
plus preferred soil texture and depth (data/crops.json). For every possible planting month
the crop's season is checked against the monthly temperatures, and yearly rainfall is
checked against the rain that actually fell in each recorded year, so unreliable rain
lowers the score. The weakest factor sets the crop's score, because one
bad factor (frost, drought, very acid soil) limits a crop however good the others are.
"""
import json
from pathlib import Path
from statistics import mean

from .climate import MONTHS, RAINY_MONTH_MM

CROPS = json.loads((Path(__file__).parent / "data" / "crops.json").read_text())["crops"]
TOP_N = 3

FACTOR_NAMES = {
    "temperature": "temperature",
    "rainfall": "rainfall",
    "ph": "soil pH",
    "texture": "soil texture",
    "depth": "soil depth",
    "altitude": "altitude",
    "dry_season": "too short a dry season",
}
ALTITUDE_MARGIN_M = 500  # the score falls from 1 at a crop's altitude limit to 0 this far above it

LIGHT_TEXTURES = {"sand", "loamy sand", "sandy loam"}
HEAVY_TEXTURES = {"clay", "silty clay", "sandy clay"}


def ramp(x, low, opt_low, opt_high, high):
    """1 inside the ideal range, falling to 0 at the absolute limits."""
    if x <= low or x >= high:
        return 0.0
    if opt_low <= x <= opt_high:
        return 1.0
    if x < opt_low:
        return (x - low) / (opt_low - low)
    return (high - x) / (high - opt_high)


def texture_group(soil):
    """iSDA texture class (or clay/sand %) -> ECOCROP's light / medium / heavy."""
    cls = (soil.get("texture_class") or "").strip().lower()
    if cls:
        if cls in LIGHT_TEXTURES:
            return "light"
        if cls in HEAVY_TEXTURES:
            return "heavy"
        return "medium"
    clay, sand = soil.get("clay_content"), soil.get("sand_content")
    if clay is None or sand is None:
        return None
    if clay >= 40:
        return "heavy"
    if sand >= 70:
        return "light"
    return "medium"


def depth_score(depth, crop):
    optimal, absolute = crop["depth_cm"]["optimal"], crop["depth_cm"]["absolute"]
    if depth is None or not optimal:
        return None
    absolute = min(absolute or optimal, optimal)
    if depth >= optimal:
        return 1.0
    if depth >= absolute:
        return 0.6 + 0.4 * (depth - absolute) / max(optimal - absolute, 1)
    return 0.3 * depth / max(absolute, 1)


def centrality(x, low, opt_low, opt_high, high):
    """How close x is to the middle of the ideal range: 1 at the centre, 0 at its edges or outside."""
    if not opt_low <= x <= opt_high or opt_high == opt_low:
        return 0.0
    centre, half = (opt_low + opt_high) / 2, (opt_high - opt_low) / 2
    return 1 - abs(x - centre) / half


def dry_months(climate):
    return sum(r < RAINY_MONTH_MM for r in climate["monthly_rainfall"])


def rainfall_fit(crop, climate):
    """
    ECOCROP rainfall ranges are yearly totals. Each of the recorded years is scored on its
    own and averaged, so a place where rain often fails scores lower than its average suggests.
    """
    totals = [sum(year) for year in climate["rain_by_year"]]
    yearly = [ramp(t, *crop["rainfall"]) for t in totals]
    return mean(yearly), sum(s >= 0.5 for s in yearly), len(yearly)


def rain_onsets(climate):
    """Months in which a rainy season starts."""
    rainy = [r >= RAINY_MONTH_MM for r in climate["monthly_rainfall"]]
    return {m for m in range(12) if rainy[m] and not rainy[m - 1]}


def season_options(crop, climate):
    """Every possible planting month with the temperature fit and rain over the crop's season."""
    n = crop["months"]
    temps, mins = climate["monthly_temperature"], climate["monthly_min_temperature"]
    killing = crop["killing_temperature"]
    options = []
    for start in range(12):
        months = [(start + i) % 12 for i in range(n)]
        temp = min(ramp(temps[m], *crop["temperature"]) for m in months)
        # Monthly average night temperatures are milder than the coldest nights, hence the margin
        if killing is not None and min(mins[m] for m in months) < killing + 4:
            temp = 0.0
        options.append({
            "month": start,
            "temperature": temp,
            "rain_mm": sum(climate["monthly_rainfall"][m] for m in months),
            "temp_range": (min(temps[m] for m in months), max(temps[m] for m in months)),
        })
    return options


def best_season(crop, climate):
    """
    The planting month whose season has the best mix of temperature and enough rain (the
    crop's share of its ideal yearly minimum); among equals, one at the start of the rains.
    Sowing needs rain, so seasons start in a rainy month wherever the place has one.
    """
    needed = crop["rainfall"][1] * crop["months"] / 12
    onsets = rain_onsets(climate)
    rainy = [r >= RAINY_MONTH_MM for r in climate["monthly_rainfall"]]
    options = season_options(crop, climate)
    if any(rainy) and not crop["perennial"]:
        options = [o for o in options if rainy[o["month"]]]

    def key(s):
        water = min(s["rain_mm"] / needed, 1.0)
        return round(min(s["temperature"], water), 2), round(s["temperature"], 2), s["month"] in onsets

    return max(options, key=key)


def planting_month(crop, season, climate):
    if not crop["perennial"]:
        return MONTHS[season["month"]]
    seasons = climate["rainy_seasons"]
    if not seasons or seasons[0] == "All year":
        return None
    return seasons[0].split("–")[0]  # plant perennials at the start of the main rains


def score_crop(crop, climate, soil):
    season = best_season(crop, climate)
    rain, good_years, years = rainfall_fit(crop, climate)
    factors = {"temperature": season["temperature"], "rainfall": rain}
    if soil.get("ph") is not None:
        factors["ph"] = ramp(soil["ph"], *crop["ph"])
    group = texture_group(soil)
    if group:
        factors["texture"] = 1.0 if group in crop["texture"]["optimal"] else \
            0.7 if group in crop["texture"]["absolute"] else 0.4
    depth = depth_score(soil.get("bedrock_depth"), crop)
    if depth is not None:
        factors["depth"] = depth
    elevation, limit = climate.get("elevation_m"), crop["max_altitude_m"]
    if elevation is not None and limit:
        factors["altitude"] = max(0.0, min(1.0, 1 - (elevation - limit) / ALTITUDE_MARGIN_M))
    if crop["dry_months"]:
        factors["dry_season"] = max(0.0, 1 - 0.3 * max(0, crop["dry_months"] - dry_months(climate)))

    score = min(factors.values())
    weakest = min(factors, key=factors.get)
    # Many crops can fit a good place perfectly; prefer those whose ideal ranges are centred on it
    centred = [centrality(mean(season["temp_range"]), *crop["temperature"]),
               centrality(climate["annual_rainfall_mm"], *crop["rainfall"])]
    if soil.get("ph") is not None:
        centred.append(centrality(soil["ph"], *crop["ph"]))
    return {
        "crop": crop,
        "score": round(score, 3),
        # Scores within 0.05 of each other count as equal before the centring tie-break
        "rank_key": (round(score * 20), round(mean(centred), 3), round(score, 3)),
        "factors": {k: round(v, 2) for k, v in factors.items()},
        "limiting_factor": FACTOR_NAMES[weakest] if factors[weakest] < 0.9 else None,
        "season": season,
        "rain_years": (good_years, years),
        "planting_month": planting_month(crop, season, climate),
        "texture_group": group,
    }


def describe(result, climate, soil):
    """A short plain-English explanation of why the crop does or does not fit."""
    crop, season, f = result["crop"], result["season"], result["factors"]
    parts = []

    if crop["perennial"]:
        parts.append(f"A perennial crop; plant at the start of the rains ({result['planting_month']})."
                     if result["planting_month"] else "A perennial crop.")
    else:
        end = MONTHS[(season["month"] + crop["months"] - 1) % 12]
        parts.append(f"Best planted in {result['planting_month']} ({result['planting_month']}–{end} season, "
                     f"about {season['rain_mm']:,.0f} mm of rain).")

    _, r_lo, r_hi, _ = crop["rainfall"]
    good_years, years = result["rain_years"]
    parts.append(f"Yearly rain averages {climate['annual_rainfall_mm']:,} mm (best {r_lo:,.0f}–{r_hi:,.0f} mm) "
                 f"and suited it in {good_years} of the last {years} years.")

    _, t_lo, t_hi, _ = crop["temperature"]
    t_min, t_max = season["temp_range"]
    temp_word = "ideal" if f["temperature"] >= 0.9 else "workable" if f["temperature"] >= 0.5 else "poor"
    temp_text = f"{t_min:.0f}°C" if round(t_min) == round(t_max) else f"{t_min:.0f}–{t_max:.0f}°C"
    parts.append(f"Average temperature {temp_text} is {temp_word} (best {t_lo:.0f}–{t_hi:.0f}°C).")

    if "ph" in f:
        _, p_lo, p_hi, _ = crop["ph"]
        ph_word = "suits it" if f["ph"] >= 0.9 else "is acceptable" if f["ph"] >= 0.5 else "is a problem"
        parts.append(f"Soil pH {soil['ph']:.1f} {ph_word} (best {p_lo:.1f}–{p_hi:.1f}).")
    if f.get("texture", 1) < 0.9:
        parts.append(f"It prefers {' or '.join(crop['texture']['optimal'])} soil; this soil is {result['texture_group']}.")
    if f.get("depth", 1) < 0.9:
        parts.append(f"The soil is shallow for it (rock at about {soil['bedrock_depth']:.0f} cm).")
    if f.get("altitude", 1) < 0.9:
        parts.append(f"At {climate['elevation_m']:,.0f} m it is above the crop's usual limit "
                     f"({crop['max_altitude_m']:,.0f} m).")
    if f.get("dry_season", 1) < 0.9:
        parts.append(f"It needs about {crop['dry_months']} dry months to flower; this place has "
                     f"{dry_months(climate)}.")

    if result["limiting_factor"]:
        parts.append(f"Main limit: {result['limiting_factor']}.")
    if crop["note"]:
        parts.append(crop["note"])
    return " ".join(parts)


def local_farming_text(share, relative):
    """How common a crop (or its MapSPAM group) is on local farmland."""
    if share is None:
        return None
    if relative >= 0.5:
        return f"Widely grown around here (about {share:.0%} of local farmland)."
    if share >= 0.02:
        return f"Grown around here (about {share:.0%} of local farmland)."
    return "Rarely grown around here, so check seed, know-how and buyers first."


def recommend(climate, soil, shares=None, alpha=1.0, top_n=TOP_N):
    """
    The top crops for this climate and soil, best first.

    With `shares` (expected share of local farmland per MapSPAM label, from prevalence.py),
    each crop's suitability is weighted by how common it is locally:
        final = suitability x (alpha + (1 - alpha) x share / largest share)
    so proven local crops rise, while a suitable crop new to the area can still appear.
    """
    from .prevalence import CROP_TO_LABEL

    results = [score_crop(c, climate, soil) for c in CROPS]
    top_share = max(shares.values()) if shares else 0
    for r in results:
        label = CROP_TO_LABEL.get(r["crop"]["key"])
        share = shares.get(label) if shares and label else None
        r["local_share"] = share
        r["relative_share"] = share / top_share if share is not None and top_share else None
        weight = 1.0 if r["relative_share"] is None else alpha + (1 - alpha) * r["relative_share"]
        r["final"] = r["score"] * weight
    results.sort(key=lambda r: (round(r["final"] * 20), r["rank_key"][1:]) if shares else r["rank_key"], reverse=True)
    top = sorted(results[:top_n], key=lambda r: r["final"], reverse=True)

    recommendations = []
    for r in top:
        explanation = describe(r, climate, soil)
        farming = local_farming_text(r["local_share"], r["relative_share"] or 0)
        recommendations.append({
            "name": f"{r['crop']['name']} ({r['crop']['swahili']})",
            "key": r["crop"]["key"],
            "score": round(r["final"], 3),
            "suitability": r["score"],
            "local_share": None if r["local_share"] is None else round(r["local_share"], 3),
            "explanation": f"{farming} {explanation}" if farming else explanation,
            "planting_month": r["planting_month"],
            "limiting_factor": r["limiting_factor"],
            "factors": r["factors"],
        })
    return recommendations


def soil_notes(soil):
    """Practical soil advice that applies whichever crop is grown."""
    notes = []
    ph = soil.get("ph")
    if ph is not None and ph < 5.5:
        notes.append(f"The soil is acidic (pH {ph:.1f}). Agricultural lime raises pH and helps most crops.")
    elif ph is not None and ph > 7.8:
        notes.append(f"The soil is alkaline (pH {ph:.1f}). Add organic matter and avoid lime.")
    n = soil.get("nitrogen_total")
    if n is not None and n < 1.0:
        notes.append(f"Nitrogen is low ({n:g} g/kg). Top-dress cereals with urea or CAN, add manure, or rotate with legumes.")
    p = soil.get("phosphorous_extractable")
    if p is not None and p < 15:
        notes.append(f"Phosphorus is low ({p:g} mg/kg). Apply DAP, TSP or Minjingu rock phosphate at planting.")
    k = soil.get("potassium_extractable")
    if k is not None and k < 80:
        notes.append(f"Potassium is low ({k:g} mg/kg). Use an NPK fertiliser or add manure and compost.")
    c = soil.get("carbon_organic")
    if c is not None and c < 10:
        notes.append(f"Organic matter is low ({c:g} g/kg carbon). Add manure, compost or crop residues.")
    slope = soil.get("slope_angle")
    if slope is not None and slope > 15:
        notes.append(f"The land is steep ({slope:g}°). Use terraces or plant along the contours to stop erosion.")
    return notes
