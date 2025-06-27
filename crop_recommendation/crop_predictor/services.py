import os
import json
import numpy as np
import pandas as pd
import joblib

<<<<<<< HEAD
# Define model, scaler, and explanation paths
BASE_MODEL_PATH = os.path.join("D:\\", 'agrosmart', 'crop_recommendation', 'crop_predictor', 'ml_models', 'crop')
MODEL_PATH = os.path.join(BASE_MODEL_PATH, "crop_recomendation.joblib")
SCALER_PATH = os.path.join(BASE_MODEL_PATH, "scaler.joblib")
EXPLANATION_PATH = os.path.join(os.path.dirname(__file__), "crop_explanations.json")

# Load crop explanations
try:
    with open(EXPLANATION_PATH, "r", encoding="utf-8") as file:
        CROP_CONDITIONS = json.load(file)
except Exception as e:
    print(f"Error loading crop explanations: {e}")
    CROP_CONDITIONS = {}

# Load the trained model
try:
    crop_model = joblib.load(MODEL_PATH)
=======

# Correct model path
model_path = os.path.join("D:\\", 'agrosmart', 'crop_recommendation', 'crop_predictor', 'ml_models', 'crop', 'crop_recomendation0.joblib')
file_path = os.path.join(os.path.dirname(__file__), 'crop_explanations.json')

with open(file_path, "r", encoding="utf-8") as file:
    CROP_CONDITIONS = json.load(file)


# Load model
try:
    crop_model = joblib.load(model_path) 
>>>>>>> beb9e6f3902f60b23d0c278d47f70d33cfd52f70
except Exception as e:
    print(f"Error loading model: {e}")
    crop_model = None

<<<<<<< HEAD
# Load the scaler
try:
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    print(f"Error loading scaler: {e}")
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
=======
def predict_crop_new(N, P, K, temperature, humidity, ph, rainfall):
    try:
        if crop_model is None:
            raise Exception("Model not loaded properly.")

        # Prepare input
        data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        df = pd.DataFrame(data, columns=[
            'Nitrogen', 'Phosphorus', 'Potassium',
            'Temperature', 'Humidity', 'pH_Value', 'Rainfall'
        ])

        # Get class probabilities
        if hasattr(crop_model, "predict_proba"):
            probabilities = crop_model.predict_proba(df)[0]
            class_labels = crop_model.classes_

            # Pair classes with probabilities and sort
            crop_scores = sorted(zip(class_labels, probabilities), key=lambda x: x[1], reverse=True)

            # Get top 2 crops
            top_crops = crop_scores[:2]

            output = {
                "recommended_crops": [ 
>>>>>>> beb9e6f3902f60b23d0c278d47f70d33cfd52f70
                    {"crop": crop, "score": round(score, 4)}
                    for crop, score in top_crops
                ]
            }
        else:
<<<<<<< HEAD
            # Fallback: predict only the best crop
            crop_prediction = crop_model.predict(scaled_df)
=======
            # Fallback: Just predict the top crop if probabilities not available
            crop_prediction = crop_model.predict(df)
>>>>>>> beb9e6f3902f60b23d0c278d47f70d33cfd52f70
            output = {
                "recommended_crops": [
                    {"crop": str(crop_prediction[0]), "score": 1.0}
                ]
            }

    except Exception as e:
        print(f"Error in predict_crop_new: {e}")
        output = {}

    return output
