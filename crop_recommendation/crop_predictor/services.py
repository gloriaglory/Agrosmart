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

        # Prepare input for prediction
        data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        df = pd.DataFrame(data, columns=[
            'Nitrogen', 'Phosphorus', 'Potassium',
            'Temperature', 'Humidity', 'pH_Value', 'Rainfall'
        ])

        # Predict crop
        crop_prediction = crop_model.predict(df)

        output = {
            "predicted_crop": str(crop_prediction[0])
        }

    except Exception as e:
        print(f"Error in predict_crop_new: {e}")
        output = {}

    return output
