#!/usr/bin/env python3
import requests
import os
from PIL import Image
import io
import numpy as np

def create_test_image():
    """
    Create a test image of a plant leaf for testing the disease detection API
    """
    # Create a simple green leaf-like image
    img = Image.new('RGB', (224, 224), color='green')
    
    # Add some texture to make it look more like a leaf
    # Draw veins
    for i in range(0, 224, 20):
        for j in range(224):
            if j % 2 == 0:
                img.putpixel((i, j), (0, 180, 0))
    
    # Draw some random spots (potential disease markers)
    for _ in range(50):
        x = np.random.randint(0, 224)
        y = np.random.randint(0, 224)
        spot_size = np.random.randint(3, 8)
        for i in range(max(0, x-spot_size), min(224, x+spot_size)):
            for j in range(max(0, y-spot_size), min(224, y+spot_size)):
                if (i-x)**2 + (j-y)**2 < spot_size**2:
                    img.putpixel((i, j), (139, 69, 19))  # Brown spots
    
    return img

def test_disease_detection_api():
    """
    Test the disease detection API endpoint with a generated test image
    """
    print("Testing plant disease detection API...")
    url = "http://localhost:8000/detector/predict/"
    
    # Create a test image
    test_img = create_test_image()
    
    # Convert to bytes for sending
    img_byte_arr = io.BytesIO()
    test_img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    # Prepare the multipart form data
    files = {
        'file': ('test_leaf.jpg', img_byte_arr, 'image/jpeg')
    }
    
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            print(f"Detected Disease: {data.get('disease')}")
            print(f"Confidence: {data.get('confidence')}")
            print(f"Description: {data.get('description')[:100]}...")  # Show just the beginning
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_disease_detection_api()
