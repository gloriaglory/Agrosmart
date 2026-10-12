"""
Builds crops.json: the growing requirements of common Tanzanian crops, taken from
the FAO ECOCROP database (via https://github.com/OpenCLIM/ecocrop).

    python crop_predictor/data/build_crops.py

Season lengths are typical for Tanzanian varieties, not ECOCROP's wide ranges.
"""
import json
import math
import re
import urllib.request
from io import StringIO
from pathlib import Path

import pandas as pd

ECOCROP_URL = "https://raw.githubusercontent.com/OpenCLIM/ecocrop/main/EcoCrop_DB.csv"
OUT = Path(__file__).with_name("crops.json")

# key, English name, Swahili name, ECOCROP scientific name, season length in days (365 = perennial), note
CROPS = [
    ("maize", "Maize", "Mahindi", "Zea mays", 120, None),
    ("rice", "Rice", "Mpunga", "Oryza sativa", 120, "Best in lowland fields that hold water, or with irrigation."),
    ("sorghum", "Sorghum", "Mtama", "Sorghum bicolor", 120, None),
    ("pearl_millet", "Pearl millet", "Uwele", "Pennisetum glaucum", 90, None),
    ("finger_millet", "Finger millet", "Ulezi", "Eleusine coracana ssp. coracana", 120, None),
    ("wheat", "Wheat", "Ngano", "Triticum aestivum", 120, None),
    ("cassava", "Cassava", "Muhogo", "Manihot esculenta", 365, None),
    ("sweet_potato", "Sweet potato", "Viazi vitamu", "Ipomoea batatas", 120, None),
    ("irish_potato", "Irish potato", "Viazi mviringo", "Solanum tuberosum", 100, None),
    ("beans", "Beans", "Maharage", "Phaseolus vulgaris", 90, None),
    ("cowpea", "Cowpea", "Kunde", "Vigna unguiculata", 90, None),
    ("pigeon_pea", "Pigeon pea", "Mbaazi", "Cajanus cajan", 180, None),
    ("green_gram", "Green gram", "Choroko", "Vigna radiata", 75, None),
    ("chickpea", "Chickpea", "Dengu", "Cicer arietinum", 100, "Often sown late in the rains to grow on stored soil moisture."),
    ("groundnut", "Groundnut", "Karanga", "Arachis hypogaea", 110, None),
    ("bambara_nut", "Bambara nut", "Njugu mawe", "Vigna subterranea", 120, None),
    ("soybean", "Soybean", "Soya", "Glycine max", 110, None),
    ("peas", "Garden peas", "Njegere", "Pisum sativum", 90, None),
    ("sunflower", "Sunflower", "Alizeti", "Helianthus annuus", 110, None),
    ("sesame", "Sesame", "Ufuta", "Sesamum indicum", 110, None),
    ("cotton", "Cotton", "Pamba", "Gossypium hirsutum", 165, None),
    ("tobacco", "Tobacco", "Tumbaku", "Nicotiana tabacum", 120, None),
    ("cashew", "Cashew", "Korosho", "Anacardium occidentale", 365, None),
    ("coffee_arabica", "Arabica coffee", "Kahawa Arabika", "Coffea arabica", 365, None),
    ("coffee_robusta", "Robusta coffee", "Kahawa Robusta", "Coffea canephora", 365, None),
    ("tea", "Tea", "Chai", "Camellia sinensis", 365, None),
    ("sugarcane", "Sugarcane", "Miwa", "Saccharum officinarum", 365, None),
    ("banana", "Banana", "Ndizi", "Musa acuminata", 365, None),
    ("tomato", "Tomato", "Nyanya", "Lycopersicon esculentum", 110, None),
    ("onion", "Onion", "Vitunguu", "Allium cepa", 120, None),
    ("cabbage", "Cabbage", "Kabichi", "Brassica oleracea var. capitata", 90, None),
    ("watermelon", "Watermelon", "Tikiti maji", "Citrullus lanatus", 85, None),
    ("avocado", "Avocado", "Parachichi", "Persea americana", 365, None),
    ("mango", "Mango", "Embe", "Mangifera indica", 365, None),
    ("orange", "Orange", "Chungwa", "Citrus sinensis", 365, None),
    ("pineapple", "Pineapple", "Nanasi", "Ananas comosus", 365, None),
]


# Local corrections where ECOCROP does not fit Tanzanian varieties.
OVERRIDES = {
    # ECOCROP only has lowland bananas; East African highland bananas (Mchare, Matoke) grow
    # well at 1,000-2,000 m on Kilimanjaro, Kagera and in the Southern Highlands.
    "banana": {"temperature": [10.0, 17.0, 30.0, 40.0], "max_altitude_m": 2400.0},
    # ECOCROP's 700 mm upper limit is far below the Lake Zone, where sorghum is grown at 800-1,000 mm.
    "sorghum": {"rainfall": [300.0, 450.0, 1000.0, 1500.0]},
    # Arabica: ideal 15-24 °C (International Coffee Organization) and 1,200-1,800 mm of rain;
    # ECOCROP's 14-28 °C would put it in hot lowlands.
    "coffee_arabica": {"temperature": [10.0, 15.0, 24.0, 30.0], "rainfall": [750.0, 1200.0, 2300.0, 4200.0]},
    # ECOCROP's 20 °C ideal minimum misses East Africa's highland tea (Mufindi, Kericho);
    # tea shoots keep growing above about 12.5 °C.
    "tea": {"temperature": [8.0, 13.0, 26.0, 35.0]},
    # Cashew and mango only flower well after a clear dry season.
    "cashew": {"dry_months": 4},
    "mango": {"dry_months": 3},
}


def min_depth(text):
    """'medium (50-150 cm)' -> 50; 'deep (>>150 cm)' -> 150."""
    if not isinstance(text, str):
        return None
    numbers = re.findall(r"\d+", text)
    return int(numbers[0]) if numbers else None


def textures(text):
    if not isinstance(text, str):
        return []
    found = [t.strip() for t in text.split(",")]
    if "wide" in found:
        return ["heavy", "medium", "light"]
    return [t for t in found if t in ("heavy", "medium", "light")]


def number(value):
    return None if value is None or (isinstance(value, float) and math.isnan(value)) else float(value)


def main():
    raw = urllib.request.urlopen(ECOCROP_URL, timeout=60).read().decode("latin-1")
    table = pd.read_csv(StringIO(raw))
    table["ScientificName"] = table["ScientificName"].str.strip()
    rows = table.set_index("ScientificName")

    crops = []
    for key, name, swahili, scientific, days, note in CROPS:
        r = rows.loc[scientific]
        text_opt, text_abs = textures(r.TEXT), textures(r.TEXTR)
        crops.append({
            "key": key, "name": name, "swahili": swahili, "scientific_name": scientific,
            "months": max(1, min(12, round(days / 30))), "perennial": days >= 365,
            "temperature": [number(r.TMIN), number(r.TOPMN), number(r.TOPMX), number(r.TMAX)],
            "rainfall": [number(r.RMIN), number(r.ROPMN), number(r.ROPMX), number(r.RMAX)],
            "ph": [number(r.PHMIN), number(r.PHOPMN), number(r.PHOPMX), number(r.PHMAX)],
            "killing_temperature": number(r.KTMP),
            "max_altitude_m": number(r.ALTMX),
            "dry_months": 0,
            "depth_cm": {"optimal": min_depth(r.DEP), "absolute": min_depth(r.DEPR)},
            # Some crops have no texture data in ECOCROP; treat every texture as acceptable
            "texture": {"optimal": text_opt or ["heavy", "medium", "light"],
                        "absolute": sorted(set(text_abs) | set(text_opt)) or ["heavy", "medium", "light"]},
            "note": note,
        })
        crops[-1].update(OVERRIDES.get(key, {}))

    OUT.write_text(json.dumps({
        "source": "FAO ECOCROP database, via github.com/OpenCLIM/ecocrop",
        "crops": crops,
    }, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {len(crops)} crops to {OUT}")


if __name__ == "__main__":
    main()
