import os
import json
import numpy as np
import pandas as pd
import joblib

# The trained Kaggle-style model (N, P, K, temperature, humidity, pH, rainfall).
# Not used for live recommendations (see suitability.py): its training data is not
# Tanzanian and its units do not match iSDA soil data. Kept for comparison.
BASE_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'crop')
MODEL_PATH = os.path.join(BASE_MODEL_PATH, "crop_recommendation_model.joblib")
META_PATH = os.path.join(BASE_MODEL_PATH, "crop_model_meta.json")
EXPLANATION_PATH = os.path.join(os.path.dirname(__file__), "crop_explanations.json")

# Load crop explanations
try:
    with open(EXPLANATION_PATH, "r", encoding="utf-8") as file:
        CROP_CONDITIONS = json.load(file)
except Exception as e:
    print(f"Error loading crop explanations: {e}")
    CROP_CONDITIONS = {}

# Load the trained model and the feature order it expects
try:
    crop_model = joblib.load(MODEL_PATH)
    with open(META_PATH, "r", encoding="utf-8") as file:
        FEATURES = json.load(file)["features"]
except Exception as e:
    print(f"Error loading model: {e}")
    crop_model, FEATURES = None, []

# How many crops to recommend
TOP_N = 3


def predict_crop_new(N, P, K, temperature, humidity, ph, rainfall):
    """
    Predicts the top crops based on soil and weather parameters.
    `rainfall` is in mm, as in the training data.
    Returns a dictionary of recommended crops with their scores.
    """
    try:
        if crop_model is None:
            raise Exception("Model not loaded properly.")
        values = [N, P, K, temperature, humidity, ph, rainfall]
        df = pd.DataFrame([dict(zip(FEATURES, values))])  # raw values, as in training

        # Use model probabilities if available
        if hasattr(crop_model, "predict_proba"):
            probabilities = crop_model.predict_proba(df)[0]
            class_labels = crop_model.classes_

            # Pair crops with their probabilities and sort by score
            crop_scores = sorted(zip(class_labels, probabilities), key=lambda x: x[1], reverse=True)
            top_crops = crop_scores[:TOP_N]

            output = {
                "recommended_crops": [
                    {"crop": crop, "score": round(score, 4)}
                    for crop, score in top_crops
                ]
            }
        else:
            # Fallback: predict only the best crop
            crop_prediction = crop_model.predict(df)
            output = {
                "recommended_crops": [
                    {"crop": str(crop_prediction[0]), "score": 1.0}
                ]
            }

    except Exception as e:
        print(f"Error in predict_crop_new: {e}")
        output = {}

    return output
