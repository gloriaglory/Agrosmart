"""
Step 1: unpack the downloaded datasets and build data/manifest.csv
(one row per photo: path, label, source, split).

    ./download_data.sh
    python prepare_data.py

Lab photos (PlantVillage) are capped per class so they do not swamp the
real-world field photos, which matter most for farmers' own pictures.
"""
import argparse
import random
import zipfile
from collections import defaultdict
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from classes import BEANS, CASSAVA, CLASS_INDEX, PLANTDOC, PLANTVILLAGE, TANZANIA_MAIZE

HERE = Path(__file__).parent
RAW = HERE / "data" / "raw"
IMAGES = HERE / "data" / "images"
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def extract(zip_name, target, members=None):
    """Unzip once into data/images/<target>; returns the folder."""
    out = IMAGES / target
    marker = out / ".extracted"
    if not marker.exists():
        print(f"extracting {zip_name} ...", flush=True)
        with zipfile.ZipFile(RAW / zip_name) as z:
            names = [n for n in z.namelist() if members is None or members(n)]
            z.extractall(out, members=names)
        marker.touch()
    return out


def images_under(folder):
    return [p for p in folder.rglob("*") if p.suffix.lower() in IMAGE_EXT and not p.name.startswith("._")]


def label_from_path(path, mapping):
    """Find the first folder name in the path that is a known label."""
    for part in reversed(path.parts[:-1]):
        key = part.lower()
        if key in mapping:
            return mapping[key]
    return None


def split_from_path(path):
    # Dataset "validation" folders become extra training data; train.py holds out its own validation
    return "test" if "test" in {p.lower() for p in path.parts} else "train"


def plantvillage(per_class_train, per_class_test, rng):
    folder = extract("plantvillage.zip", "plantvillage", members=lambda n: "/color/" in f"/{n}")
    by_name = {(p.parent.name, p.name): p for p in images_under(folder)}
    rows = []
    for split, file, cap in [("train", "pv_color_train.txt", per_class_train), ("test", "pv_color_test.txt", per_class_test)]:
        per_class = defaultdict(list)
        for line in filter(None, (RAW / file).read_text().splitlines()):  # names contain spaces
            label = Path(line.strip()).parent.name
            path = by_name.get((label, Path(line.strip()).name))
            if path and label in PLANTVILLAGE:
                per_class[label].append(path)
        for label, paths in per_class.items():
            rng.shuffle(paths)
            rows += [dict(path=str(p), label=label, source="plantvillage", split=split) for p in paths[:cap]]
    return rows


def plantdoc():
    out = IMAGES / "plantdoc"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for part in sorted(RAW.glob("plantdoc_*.parquet")):
        table = pq.read_table(part, columns=["image", "class_label", "split", "filename"]).to_pylist()
        for i, item in enumerate(table):
            label = PLANTDOC.get(item["class_label"])
            if not label:
                continue
            path = out / f"{part.stem}_{i:05d}.jpg"
            if not path.exists():
                path.write_bytes(item["image"]["bytes"])
            rows.append(dict(path=str(path), label=label, source="plantdoc",
                             split="test" if item["split"] == "test" else "train"))
    return rows


def folder_dataset(zip_name, name, mapping, cap_train, rng):
    folder = extract(zip_name, name)
    per = defaultdict(list)
    for p in images_under(folder):
        label = label_from_path(p, mapping)
        if label:
            per[(label, split_from_path(p))].append(p)
    rows = []
    for (label, split), paths in per.items():
        rng.shuffle(paths)
        keep = paths[:cap_train] if (split == "train" and cap_train) else paths
        rows += [dict(path=str(p), label=label, source=name, split=split) for p in keep]
    return rows


def tanzania_maize(cap_train, cap_test, rng):
    """The Zenodo parts have no train/test split; hold out a random share of each class."""
    rows = []
    for key, label in TANZANIA_MAIZE.items():
        zip_name = f"tz_{key}1.zip"
        if not (RAW / zip_name).exists():
            print(f"missing {zip_name}, skipping")
            continue
        paths = images_under(extract(zip_name, f"tanzania_maize/{key}"))
        rng.shuffle(paths)
        test, train = paths[:cap_test], paths[cap_test:cap_test + cap_train]
        rows += [dict(path=str(p), label=label, source="tanzania_maize", split="test") for p in test]
        rows += [dict(path=str(p), label=label, source="tanzania_maize", split="train") for p in train]
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pv-train", type=int, default=500, help="PlantVillage training photos per class")
    parser.add_argument("--pv-test", type=int, default=60, help="PlantVillage test photos per class")
    parser.add_argument("--cassava-train", type=int, default=900, help="cassava training photos per class")
    parser.add_argument("--tz-train", type=int, default=1500, help="Tanzania maize training photos per class")
    parser.add_argument("--tz-test", type=int, default=250, help="Tanzania maize test photos per class")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    rng = random.Random(args.seed)

    rows = []
    rows += plantdoc()
    rows += folder_dataset("beans_train.zip", "beans", BEANS, None, rng)
    rows += [dict(r, split="test") for r in folder_dataset("beans_test.zip", "beans_test", BEANS, None, rng)]
    rows += [dict(r, split="test") for r in folder_dataset("beans_validation.zip", "beans_validation", BEANS, None, rng)]
    for r in rows:  # the bean test/validation zips are their own sources only for extraction
        if r["source"].startswith("beans"):
            r["source"] = "beans"
    rows += folder_dataset("cassava.zip", "cassava", CASSAVA, args.cassava_train, rng)
    rows += tanzania_maize(args.tz_train, args.tz_test, rng)
    rows += plantvillage(args.pv_train, args.pv_test, rng)

    manifest = pd.DataFrame(rows)
    unknown = set(manifest.label) - set(CLASS_INDEX)
    assert not unknown, f"labels not in classes.py: {unknown}"
    manifest.to_csv(HERE / "data" / "manifest.csv", index=False)

    print(f"\nmanifest: {len(manifest)} photos, {manifest.label.nunique()} classes")
    print(manifest.groupby(["source", "split"]).size().unstack(fill_value=0).to_string())
    missing = sorted(set(CLASS_INDEX) - set(manifest.label))
    if missing:
        print("classes with no photos:", missing)


if __name__ == "__main__":
    main()
