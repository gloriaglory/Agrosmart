import os
import zipfile
import json
import numpy as np
import requests
from PIL import Image
import tensorflow as tf

# === Download Helper Functions ===

def download_from_google_drive(file_id: str, dest_path: str):
    """Downloads a file from Google Drive using a confirmation token if necessary."""
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={"id": file_id}, stream=True)
    token = _get_confirm_token(response)

    if token:
        response = session.get(URL, params={"id": file_id, "confirm": token}, stream=True)

    _save_response_content(response, dest_path)

def _get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None

def _save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

# === Paths and Constants ===

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_NAME = "plant_disease_model1.keras"
MODEL_PATH = os.path.join(BASE_DIR, "disease_detection", "ml_models", MODEL_NAME)
ZIP_PATH = MODEL_PATH + ".zip"
DISEASE_INFO_PATH = os.path.join(BASE_DIR, "disease_detection", "ml_models", "disease_info.json")
GOOGLE_DRIVE_FILE_ID = "1dZbPBuPFqyYjvBOXBnEuT4GE9RsdS-4F"

# === Model Setup ===

def ensure_model_exists():
    """Download and unzip the model if it doesn't already exist."""
    if not os.path.exists(MODEL_PATH):
        if not os.path.exists(ZIP_PATH):
            print("Downloading model from Google Drive...")
            try:
                download_from_google_drive(GOOGLE_DRIVE_FILE_ID, ZIP_PATH)
                print("Model zip downloaded.")
            except Exception as e:
                print(f"Failed to download model zip: {e}")
                return

        print("Extracting model zip...")
        try:
            with zipfile.ZipFile(ZIP_PATH, 'r') as zipf:
                zipf.extractall(os.path.dirname(MODEL_PATH))
            print("Model extracted.")
        except Exception as e:
            print(f"Failed to unzip model: {e}")

# Ensure model is ready
ensure_model_exists()

# Load model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Load disease info
try:
    with open(DISEASE_INFO_PATH, "r", encoding="utf-8") as f:
        disease_data = json.load(f)
        disease_info = disease_data["diseases"]
        CLASS_NAMES = list(disease_info.keys())
except Exception as e:
    print(f"Error loading disease info: {e}")
    disease_info = {}
    CLASS_NAMES = []

# === Image Preprocessing ===

def preprocess_image(image: Image.Image, target_size=(224, 224)) -> np.ndarray:
    """Resize and normalize image to model's input format."""
    image = image.resize(target_size)
    img_array = np.array(image) / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# === Prediction ===

def predict_disease(image_file) -> dict:
    """Predict plant disease from an image file."""
    if model is None:
        raise RuntimeError("Model not loaded.")
    
    if not CLASS_NAMES:
        raise RuntimeError("CLASS_NAMES list is empty. Check disease_info.json format.")

    # Open and preprocess the image
    image = Image.open(image_file).convert("RGB")
    processed_img = preprocess_image(image)

    # Predict
    predictions = model.predict(processed_img)[0]
    pred_idx = int(np.argmax(predictions))

    # Fallback in case of mismatch
    if pred_idx >= len(CLASS_NAMES):
        pred_idx = int(np.argmax(predictions[:len(CLASS_NAMES)]))

    disease_name = CLASS_NAMES[pred_idx]
    confidence = float(predictions[pred_idx])
    disease_details = disease_info.get(disease_name, {})

    return {
        "disease": disease_name,
        "confidence": round(confidence, 4),
        "description": disease_details.get("description", "No description available."),
        "treatment": disease_details.get("treatment", "No treatment specified."),
        "preventive_measures": disease_details.get("preventive_measures", "No preventive measures specified.")
    }
