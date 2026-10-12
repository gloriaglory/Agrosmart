"""
Step 3: train the classifier on the features, test it, and export the full model.

    python train.py                         # uses data/features_b0.npz
    python train.py --backbone s            # after `python embed.py --backbone s`

Writes runs/<timestamp>/ with disease_model.keras, model_config.json and metrics.json.
"""
import argparse
import json
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf

from classes import CLASSES, FIELD_SOURCES
from embed import build_backbone
from preprocess import IMAGE_SIZE, load_for_model

HERE = Path(__file__).parent
crop_of = lambda name: name.split("___")[0]


def split_validation(photo, labels, train_mask, fraction, seed):
    """Hold out whole photos (all their altered copies together) for validation."""
    rng = np.random.default_rng(seed)
    val_photos = set()
    for label in np.unique(labels[train_mask]):
        photos = np.unique(photo[train_mask & (labels == label)])
        n = max(1, int(len(photos) * fraction))
        val_photos.update(rng.choice(photos, size=n, replace=False).tolist())
    is_val = np.isin(photo, list(val_photos)) & train_mask
    return train_mask & ~is_val, is_val


def build_head(n_features, n_classes):
    inputs = tf.keras.Input((n_features,))
    x = tf.keras.layers.Dropout(0.3)(inputs)
    x = tf.keras.layers.Dense(512, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(n_classes, activation="softmax")(x)
    return tf.keras.Model(inputs, outputs, name="disease_head")


def evaluate(probs, labels, sources):
    pred = probs.argmax(1)
    top3 = np.argsort(probs, 1)[:, ::-1][:, :3]
    report = {}
    for group, mask in [("field (real-world)", np.isin(sources, list(FIELD_SOURCES))),
                        ("lab (PlantVillage)", sources == "plantvillage"),
                        *[(s, sources == s) for s in sorted(set(sources))]]:
        if not mask.any():
            continue
        report[group] = {
            "photos": int(mask.sum()),
            "accuracy": round(float((pred[mask] == labels[mask]).mean()), 4),
            "top3_accuracy": round(float((top3[mask] == labels[mask, None]).any(1).mean()), 4),
            "right_crop": round(float(np.mean([crop_of(CLASSES[p]) == crop_of(CLASSES[t])
                                               for p, t in zip(pred[mask], labels[mask])])), 4),
        }
    per_class = {}
    for c in np.unique(labels):
        mask = labels == c
        per_class[CLASSES[c]] = {"photos": int(mask.sum()), "accuracy": round(float((pred[mask] == c).mean()), 3)}
    mistakes = Counter((CLASSES[t], CLASSES[p]) for t, p in zip(labels, pred) if t != p).most_common(12)
    return report, per_class, [{"true": t, "predicted": p, "count": n} for (t, p), n in mistakes]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backbone", default="b0")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--field-weight", type=float, default=2.0, help="extra weight for real-world photos")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    tf.keras.utils.set_random_seed(args.seed)

    data = np.load(HERE / f"data/features_{args.backbone}.npz", allow_pickle=True)
    x, y = data["features"].astype(np.float32), data["labels"]
    photo, view, split, source = data["photo"], data["view"], data["split"], data["source"]

    train_mask, val_mask = split_validation(photo, y, split == "train", 0.1, args.seed)
    val_mask &= view == 0
    test_mask = (split == "test") & (view == 0)
    print(f"train vectors {train_mask.sum()}, validation photos {val_mask.sum()}, test photos {test_mask.sum()}")

    # Balance classes, and count real-world photos extra so the model does not just learn lab photos
    counts = Counter(y[train_mask])
    class_w = {c: len(y[train_mask]) / (len(counts) * n) for c, n in counts.items()}
    weights = np.array([class_w[c] for c in y[train_mask]])
    weights *= np.where(np.isin(source[train_mask], list(FIELD_SOURCES)), args.field_weight, 1.0)

    head = build_head(x.shape[1], len(CLASSES))
    head.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    head.fit(
        x[train_mask], y[train_mask], sample_weight=weights,
        validation_data=(x[val_mask], y[val_mask]),
        epochs=args.epochs, batch_size=256, verbose=2,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True),
            tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=3),
        ],
    )

    report, per_class, mistakes = evaluate(head.predict(x[test_mask], verbose=0), y[test_mask], source[test_mask])
    print(json.dumps(report, indent=2))

    # Export one model that takes a 224x224 photo (0-255 pixels) and returns class probabilities
    backbone = build_backbone(args.backbone)
    inputs = tf.keras.Input((IMAGE_SIZE, IMAGE_SIZE, 3), name="image")
    full = tf.keras.Model(inputs, head(backbone(inputs)), name="agrosmart_disease")

    run = HERE / "runs" / datetime.now().strftime("%Y%m%d-%H%M%S")
    run.mkdir(parents=True)
    full.save(run / "disease_model.keras")
    config = {
        "model_file": "disease_model.keras",
        "backbone": backbone.name,
        "input_size": IMAGE_SIZE,
        "pixel_range": "0-255",
        "preprocessing": "EXIF rotation, RGB, Lanczos resize to input_size (ml/disease/preprocess.py)",
        "classes": CLASSES,
        "trained_at": datetime.now().isoformat(timespec="seconds"),
    }
    (run / "model_config.json").write_text(json.dumps(config, indent=2))
    (run / "metrics.json").write_text(json.dumps(
        {"summary": report, "per_class": per_class, "top_mistakes": mistakes, "args": vars(args)}, indent=2))

    # Sanity check: the exported model must agree with the head on a few test photos
    manifest = pd.read_csv(HERE / "data/manifest.csv")
    sample = np.where(test_mask)[0][:16]
    images = np.stack([load_for_model(manifest.path[photo[i]]) for i in sample])
    agree = (full.predict(images, verbose=0).argmax(1) == head.predict(x[sample], verbose=0).argmax(1)).mean()
    print(f"export check: exported model agrees with trained head on {agree:.0%} of sample photos")
    print(f"saved to {run}")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"done in {(time.time() - start) / 60:.1f} min")
