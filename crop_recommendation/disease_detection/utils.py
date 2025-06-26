import os
import numpy as np
from PIL import Image
import tensorflow as tf
import json

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "disease_detection", "ml_models", "plant_disease_model.keras")
DISEASE_INFO_PATH = os.path.join(BASE_DIR, "disease_detection", "ml_models", "disease_info.json")

# Load Keras model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Load disease information
try:
    with open(DISEASE_INFO_PATH, "r", encoding="utf-8") as file:
        disease_info = json.load(file)
except Exception as e:
    print(f"Error loading disease info: {e}")
    disease_info = {}

# Get class names from the JSON keys
CLASS_NAMES = list(disease_info.keys())

def preprocess_image(image: Image.Image, target_size=(224, 224)) -> np.ndarray:
    """
    Preprocess the uploaded image to match the model input.
    """
    image = image.resize(target_size)
    img_array = np.array(image)
    img_array = img_array / 255.0  # Normalize to [0,1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

def predict_disease(image_file) -> dict:
    """
    Predict the disease class from the uploaded image.
    """
    if model is None:
        raise Exception("Model not loaded properly.")

    # Open and preprocess the image
    image = Image.open(image_file).convert("RGB")
    processed_img = preprocess_image(image)

    # Predict using the loaded model
    predictions = model.predict(processed_img)
    predictions = predictions[0]  # Extract first (and only) batch prediction

    # Get the most probable disease class
    pred_idx = int(np.argmax(predictions))
    disease_name = CLASS_NAMES[pred_idx]
    confidence = float(predictions[pred_idx])

    # Get disease details
    disease_details = disease_info.get(disease_name, {})

    return {
        "disease": disease_name,
        "confidence": round(confidence, 4),
        "description": disease_details.get("description", "No description available."),
        "treatment": disease_details.get("treatment", "No treatment specified."),
        "preventive_measures": disease_details.get("preventive_measures", "No preventive measures specified.")
    }
