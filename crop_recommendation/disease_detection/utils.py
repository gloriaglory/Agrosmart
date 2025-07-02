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

    predictions = model.predict(processed_img)[0]
    pred_idx = int(np.argmax(predictions))

    if pred_idx >= len(CLASS_NAMES):
        pred_idx = int(np.argmax(predictions[:len(CLASS_NAMES)]))

    disease_name = CLASS_NAMES[pred_idx]
    confidence = float(predictions[pred_idx])
    disease_details = DISEASE_INFO.get(disease_name, {})

    return {
        "disease": disease_name,
        "confidence": round(confidence, 4),
        "description": disease_details.get("description", "No description available."),
        "treatment": disease_details.get("treatment", "No treatment specified."),
        "preventive_measures": disease_details.get("preventive_measures", "No preventive measures specified.")
    }
