import os
import zipfile
import numpy as np
import requests
from PIL import Image
import tensorflow as tf
import json

# Google Drive Download Logic 
def download_from_google_drive(file_id, dest_path):
    """Downloads a file from Google Drive handling confirmation token."""
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    
    response = session.get(URL, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)
    
    if token:
        response = session.get(URL, params={"id": file_id, "confirm": token}, stream=True)
    
    save_response_content(response, dest_path)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "disease_detection", "ml_models", "plant_disease_model.keras")
ZIP_PATH = MODEL_PATH + ".zip"
DISEASE_INFO_PATH = os.path.join(BASE_DIR, "disease_detection", "ml_models", "disease_info.json")

# Download model zip from Google Drive 
if not os.path.exists(MODEL_PATH):
    if not os.path.exists(ZIP_PATH):
        print("Downloading model...")
        FILE_ID = "1dZbPBuPFqyYjvBOXBnEuT4GE9RsdS-4F"  
        try:
            download_from_google_drive(FILE_ID, ZIP_PATH)
            print("Model zip downloaded.")
        except Exception as e:
            print(f"Failed to download model zip: {e}")

    # Decompress
    if os.path.exists(ZIP_PATH):
        print("Extracting model zip...")
        try:
            with zipfile.ZipFile(ZIP_PATH, 'r') as zipf:
                zipf.extractall(os.path.dirname(MODEL_PATH))
            print("Model extracted.")
        except Exception as e:
            print(f"Failed to unzip model: {e}")
    else:
        print("Model zip not found, cannot continue.")

# Load model 
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Load disease info
try:
    with open(DISEASE_INFO_PATH, "r", encoding="utf-8") as file:
        disease_info = json.load(file)
except Exception as e:
    print(f"Error loading disease info: {e}")
    disease_info = {}

# Class names 
CLASS_NAMES = list(disease_info.keys())

#Image Preprocessing 
def preprocess_image(image: Image.Image, target_size=(224, 224)) -> np.ndarray:
    image = image.resize(target_size)
    img_array = np.array(image)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

# Prediction 
def predict_disease(image_file) -> dict:
    if model is None:
        raise Exception("Model not loaded.")

    image = Image.open(image_file).convert("RGB")
    processed_img = preprocess_image(image)

    predictions = model.predict(processed_img)
    predictions = predictions[0]

    pred_idx = int(np.argmax(predictions))
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
