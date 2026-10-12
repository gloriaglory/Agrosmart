"""
Step 2: turn every photo in the manifest into a feature vector with a pretrained backbone.

Training photos from field datasets get extra randomly altered copies ("views"),
so the classifier learns real-world variation. Test photos get exactly the
preparation the live app uses.

    python embed.py                      # uses data/manifest.csv, writes data/features_b0.npz
"""
import argparse
import random
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf

from classes import CLASS_INDEX, FIELD_SOURCES
from preprocess import augmented, load_for_model

HERE = Path(__file__).parent
BACKBONES = {
    "b0": tf.keras.applications.EfficientNetV2B0,
    "s": tf.keras.applications.EfficientNetV2S,
}


def build_backbone(name):
    # EfficientNetV2 includes its own input scaling, so it takes raw 0-255 pixels
    return BACKBONES[name](include_top=False, weights="imagenet", pooling="avg",
                           input_shape=(224, 224, 3))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(HERE / "data/manifest.csv"))
    parser.add_argument("--backbone", default="b0", choices=BACKBONES)
    parser.add_argument("--field-views", type=int, default=3, help="extra altered copies per field training photo")
    parser.add_argument("--lab-views", type=int, default=1, help="extra altered copies per lab (PlantVillage) training photo")
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)
    jobs = []  # (row index, view number); view 0 is the plain, app-identical preparation
    for i, row in manifest.iterrows():
        jobs.append((i, 0))
        if row.split == "train":
            extra = args.field_views if row.source in FIELD_SOURCES else args.lab_views
            jobs.extend((i, v) for v in range(1, extra + 1))
    print(f"{len(manifest)} photos -> {len(jobs)} feature vectors with backbone {args.backbone}")

    model = build_backbone(args.backbone)
    paths = manifest.path.tolist()

    def load(job):
        i, view = job
        try:
            if view == 0:
                return load_for_model(paths[i])
            return augmented(paths[i], random.Random(f"{args.seed}-{i}-{view}"))
        except Exception as exc:
            print(f"  skipping unreadable {paths[i]}: {exc}")
            return None

    features, rows, views = [], [], []
    start = time.time()
    with ThreadPoolExecutor(max_workers=8) as pool:
        for b in range(0, len(jobs), args.batch):
            batch = jobs[b:b + args.batch]
            images = list(pool.map(load, batch))
            keep = [(job, img) for job, img in zip(batch, images) if img is not None]
            if not keep:
                continue
            x = np.stack([img for _, img in keep])
            features.append(model.predict(x, verbose=0).astype(np.float16))
            rows.extend(job[0] for job, _ in keep)
            views.extend(job[1] for job, _ in keep)
            done = b + len(batch)
            if (b // args.batch) % 20 == 0:
                rate = done / (time.time() - start)
                print(f"  {done}/{len(jobs)}  {rate:.0f}/s  ~{(len(jobs) - done) / rate / 60:.1f} min left", flush=True)

    rows = np.array(rows)
    out = Path(args.manifest).with_name(f"features_{args.backbone}.npz")
    np.savez_compressed(
        out,
        features=np.concatenate(features),
        labels=manifest.label.map(CLASS_INDEX).to_numpy()[rows],
        photo=rows,
        view=np.array(views),
        split=manifest.split.to_numpy()[rows],
        source=manifest.source.to_numpy()[rows],
    )
    print(f"saved {len(rows)} feature vectors to {out} in {(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
