"""
Image preparation shared by training and the AgroSmart backend.

The live app (crop_recommendation/disease_detection/utils.py) must prepare photos
exactly like `load_for_model` does here, or accuracy silently drops.
"""
import io
import random

import numpy as np
from PIL import Image, ImageEnhance, ImageOps

IMAGE_SIZE = 224


def open_rgb(source):
    """Open a path, bytes or file object as an upright RGB image (phone rotation applied)."""
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    img = Image.open(source)
    img = ImageOps.exif_transpose(img)
    return img.convert("RGB")


def load_for_model(source, size=IMAGE_SIZE):
    """The exact preparation used at prediction time: upright, RGB, smooth resize, 0-255 floats."""
    img = open_rgb(source).resize((size, size), Image.LANCZOS)
    return np.asarray(img, dtype=np.float32)


def augmented(source, rng: random.Random, size=IMAGE_SIZE):
    """A randomly altered copy for training, mimicking how farmers take photos."""
    img = open_rgb(source)
    w, h = img.size

    # Random crop of 55-100% of the photo with a slightly varied shape
    for _ in range(10):
        area = rng.uniform(0.55, 1.0) * w * h
        ratio = rng.uniform(3 / 4, 4 / 3)
        cw, ch = int(round((area * ratio) ** 0.5)), int(round((area / ratio) ** 0.5))
        if 0 < cw <= w and 0 < ch <= h:
            x, y = rng.randint(0, w - cw), rng.randint(0, h - ch)
            img = img.crop((x, y, x + cw, y + ch))
            break

    if rng.random() < 0.5:
        img = ImageOps.mirror(img)
    if rng.random() < 0.5:
        img = ImageOps.flip(img)
    img = img.rotate(rng.choice([0, 90, 180, 270]) + rng.uniform(-15, 15), resample=Image.BILINEAR, expand=False)

    for enhancer in (ImageEnhance.Brightness, ImageEnhance.Contrast, ImageEnhance.Color):
        img = enhancer(img).enhance(rng.uniform(0.75, 1.25))

    img = img.resize((size, size), Image.LANCZOS)
    return np.asarray(img, dtype=np.float32)
