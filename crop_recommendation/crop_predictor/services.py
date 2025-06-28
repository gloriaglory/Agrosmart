import os
import json
import numpy as np
import pandas as pd
import joblib

# Define model, scaler, and explanation paths using relative paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_MODEL_PATH = os.path.join(BASE_DIR, 'ml_model', 'crop')
MODEL_PATH = os.path.join(BASE_MODEL_PATH, "crop_recomendation.joblib")
SCALER_PATH = os.path.join(BASE_MODEL_PATH, "scaler.joblib")
EXPLANATION_PATH = os.path.join(os.path.dirname(__file__), "crop_explanations.json")

# Print absolute paths for debugging
print("="*80)
print(f"Current working directory: {os.getcwd()}")
print(f"BASE_DIR: {BASE_DIR}")
print(f"BASE_MODEL_PATH: {BASE_MODEL_PATH}")
print(f"MODEL_PATH: {MODEL_PATH}")
print(f"SCALER_PATH: {SCALER_PATH}")
print(f"EXPLANATION_PATH: {EXPLANATION_PATH}")
print("="*80)

# Check if model path exists
if os.path.exists(MODEL_PATH):
    print(f"✓ Model file exists at: {MODEL_PATH}")
else:
    print(f"✗ Model file NOT FOUND at: {MODEL_PATH}")

# Check if scaler path exists
if os.path.exists(SCALER_PATH):
    print(f"✓ Scaler file exists at: {SCALER_PATH}")
else:
    print(f"✗ Scaler file NOT FOUND at: {SCALER_PATH}")

# List directory contents for debugging
try:
    if os.path.exists(BASE_MODEL_PATH):
        print(f"Contents of {BASE_MODEL_PATH}:")
        for file in os.listdir(BASE_MODEL_PATH):
            print(f" - {file}")
    else:
        print(f"Directory {BASE_MODEL_PATH} does not exist!")
except Exception as e:
    print(f"Error listing directory contents: {e}")
print("="*80)

# Load crop explanations
try:
    with open(EXPLANATION_PATH, "r", encoding="utf-8") as file:
        CROP_CONDITIONS = json.load(file)
        print(f"Successfully loaded crop explanations from {EXPLANATION_PATH}")
except Exception as e:
    print(f"Error loading crop explanations: {e}")
    CROP_CONDITIONS = {}

# Load the trained model
try:
    print(f"Attempting to load model from: {MODEL_PATH}")
    crop_model = joblib.load(MODEL_PATH)
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    crop_model = None

# Load the scaler
try:
    print(f"Attempting to load scaler from: {SCALER_PATH}")
    scaler = joblib.load(SCALER_PATH)
    print("✓ Scaler loaded successfully")
except Exception as e:
    print(f"✗ Error loading scaler: {e}")
    scaler = None

def predict_crop_new(N, P, K, temperature, humidity, ph, rainfall):
    """
    Predicts the top crop(s) based on soil and weather parameters.
    Returns a dictionary of recommended crops with their scores.
    """
    try:
        if crop_model is None:
            raise Exception("Model not loaded properly.")
        if scaler is None:
            raise Exception("Scaler not loaded properly.")

        # Prepare input data as a DataFrame with correct feature names
        df = pd.DataFrame([{
            "Nitrogen": N,
            "Phosphorus": P,
            "Potassium": K,
            "Temperature": temperature,
            "Humidity": humidity,
            "pH_Value": ph,
            "Rainfall": rainfall
        }])

        print(f"Model Input: {df.values.tolist()}")

        # Apply scaler (pass DataFrame to scaler to retain feature names)
        scaled_df = scaler.transform(df)

        # Pass scaled data as DataFrame (optional but cleaner)
        scaled_df = pd.DataFrame(scaled_df, columns=df.columns)

        # Use model probabilities if available
        if hasattr(crop_model, "predict_proba"):
            probabilities = crop_model.predict_proba(scaled_df)[0]
            class_labels = crop_model.classes_

            # Pair crops with their probabilities and sort by score
            crop_scores = sorted(zip(class_labels, probabilities), key=lambda x: x[1], reverse=True)
            top_crops = crop_scores[:2]  # Get top 2

            output = {
                "recommended_crops": [
                    {"crop": crop, "score": round(score, 4)}
                    for crop, score in top_crops
                ]
            }
        else:
            # Fallback: predict only the best crop
            crop_prediction = crop_model.predict(scaled_df)
            output = {
                "recommended_crops": [
                    {"crop": str(crop_prediction[0]), "score": 1.0}
                ]
            }

    except Exception as e:
        print(f"Error in predict_crop_new: {e}")
        output = {}

    return output