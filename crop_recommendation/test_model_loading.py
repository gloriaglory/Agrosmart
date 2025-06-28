import os
import sys
from disease_detection.utils import MODEL_PATH, model

print("Testing model loading...")
print(f"Model path: {MODEL_PATH}")
print(f"Model exists: {os.path.exists(MODEL_PATH)}")
print(f"Model loaded: {model is not None}")

if model is not None:
    print("Model summary:")
    model.summary()
else:
    print("Model failed to load.")
    sys.exit(1)

print("Test completed successfully.")