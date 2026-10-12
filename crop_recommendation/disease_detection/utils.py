import os
import json
import numpy as np
import tensorflow as tf
from PIL import Image
import cv2
import tempfile

# === Paths ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "disease_detection", "ml_models", "plant_disease_model1.keras")
DISEASE_INFO_PATH = os.path.join(BASE_DIR, "disease_detection", "ml_models", "disease_info.json")
CLASS_INDICES_PATH = os.path.join(BASE_DIR, "disease_detection", "ml_models", "class_indices.json")

# === Load Model ===
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# === Load Disease Info ===
try:
    with open(DISEASE_INFO_PATH, "r", encoding="utf-8") as f:
        DISEASE_INFO = json.load(f)
except Exception as e:
    print(f"Error loading disease info: {e}")
    DISEASE_INFO = {}

# === Load Class Names using class_indices.json ===
try:
    with open(CLASS_INDICES_PATH, "r", encoding="utf-8") as f:
        class_indices = json.load(f)
        CLASS_NAMES = [None] * len(class_indices)
        for name, idx in class_indices.items():
            CLASS_NAMES[idx] = name
except Exception as e:
    print(f"Error loading class indices: {e}")
    CLASS_NAMES = []

# === Image Validation ===
def is_valid_plant_image(image_path: str, green_threshold=2.0) -> bool:
    """Check if image contains at least `green_threshold`% green pixels."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Broaden green range to include more shades
        lower_green = np.array([25, 40, 40])
        upper_green = np.array([90, 255, 255])
        
        mask = cv2.inRange(hsv, lower_green, upper_green)
        green_pixels = np.sum(mask > 0)
        total_pixels = img.shape[0] * img.shape[1]
        green_pct = (green_pixels / total_pixels) * 100
        
        print(f"Green pixels: {green_pct:.2f}%")
        return green_pct >= green_threshold
    except Exception as e:
        print(f"Image validation error: {e}")
        return False

# === Image Preprocessing ===
def preprocess_image(image_path_or_file, target_size=(224, 224)) -> np.ndarray:
    """Resize and normalize image for model input."""
    if isinstance(image_path_or_file, str):
        img = cv2.imread(image_path_or_file)
        if img is None:
            raise ValueError("Cannot read image at path")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        pil_img = Image.open(image_path_or_file).convert("RGB")
        img = np.array(pil_img)

    img = cv2.resize(img, target_size)
    img = img / 255.0
    return np.expand_dims(img, axis=0)

# === Prediction ===
def predict_disease(image_file) -> dict:
    if model is None:
        raise RuntimeError("Model not loaded.")
    if not CLASS_NAMES:
        raise RuntimeError("CLASS_NAMES is empty. Check class_indices.json.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_file.read())
        tmp.flush()
        tmp_path = tmp.name

    try:
        if not is_valid_plant_image(tmp_path):
            raise ValueError("Image is not a plant.")
        image_file.seek(0)
        processed_img = preprocess_image(image_file)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    predictions = model.predict(processed_img, verbose=0)[0]
    return build_result(predictions)


# Below this confidence the result is shown as "not sure" instead of a diagnosis
# (same idea as the Plant-Disease-Detection project's 0.4 threshold).
CONFIDENCE_THRESHOLD = 0.4
TOP_N = 3

# Shown with every diagnosis: photo-based detection can be wrong, and a wrong
# diagnosis can lead to the wrong pesticide being sprayed.
CAUTION = (
    "This result is a guide only. Photo-based detection can be wrong, so confirm "
    "with an agricultural extension officer before buying or spraying any pesticide."
)


def _paragraph(value):
    """The UI shows treatment and prevention as one paragraph; the data stores them as steps."""
    if isinstance(value, list):
        return " ".join(step.strip() for step in value if step.strip())
    return value or ""


def build_result(predictions) -> dict:
    """Turn model output into the response the disease detection page expects."""
    predictions = np.asarray(predictions[: len(CLASS_NAMES)], dtype=float)
    order = np.argsort(predictions)[::-1]
    top = [
        {
            "class": CLASS_NAMES[i],
            "name": DISEASE_INFO.get(CLASS_NAMES[i], {}).get("name", CLASS_NAMES[i]),
            "confidence": round(float(predictions[i]), 4),
        }
        for i in order[:TOP_N]
    ]
    best = top[0]
    details = DISEASE_INFO.get(best["class"], {})

    if best["confidence"] < CONFIDENCE_THRESHOLD:
        return {
            "disease": "Not sure",
            "confidence": best["confidence"],
            "uncertain": True,
            "description": (
                "The photo is not clear enough for a confident result. The closest matches were: "
                + ", ".join(f"{t['name']} ({t['confidence'] * 100:.0f}%)" for t in top)
                + ". Take a new photo of a single leaf, close up, in daylight, against a plain background."
            ),
            "treatment": "Do not treat yet. Retake the photo, or show the plant to an extension officer to confirm the problem.",
            "preventive_measures": "Check your plants every week so problems are caught early.",
            "top_predictions": top,
        }

    return {
        "disease": details.get("name", best["class"]),
        "class": best["class"],
        "crop": details.get("crop", ""),
        "type": details.get("type", ""),
        "confidence": best["confidence"],
        "uncertain": False,
        "description": f"{details.get('description') or 'No description available.'} {CAUTION}",
        "treatment": _paragraph(details.get("treatment")) or "No treatment specified.",
        "preventive_measures": _paragraph(details.get("prevention")) or "No preventive measures specified.",
        "top_predictions": top,
    }
