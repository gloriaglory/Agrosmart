import os
import json
import numpy as np
import pandas as pd
import joblib


# Correct model path
model_path = os.path.join("D:\\", 'agrosmart', 'crop_recommendation', 'crop_predictor', 'ml_models', 'crop', 'crop_recomendation0.joblib')
file_path = os.path.join(os.path.dirname(__file__), 'crop_explanations.json')

with open(file_path, "r", encoding="utf-8") as file:
    CROP_CONDITIONS = json.load(file)


# Load model
try:
    crop_model = joblib.load(model_path) 
except Exception as e:
    print(f"Error loading model: {e}")
    crop_model = None

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
                    {"crop": crop, "score": round(score, 4)}
                    for crop, score in top_crops
                ]
            }
        else:
            # Fallback: Just predict the top crop if probabilities not available
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
