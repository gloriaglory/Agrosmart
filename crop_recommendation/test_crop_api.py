#!/usr/bin/env python3
import requests
import json

def test_crop_recommendation_api():
    """
    Test the crop recommendation API endpoint
    """
    print("Testing crop recommendation API...")
    url = "http://localhost:8000/api/recommend/"
    
    payload = {
        "address": "Nairobi, Kenya"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            print("Recommendations:")
            for crop, details in data["recommendations"].items():
                print(f"- {crop}: Score {details['score']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_simple_crop_recommendation_api():
    """
    Test the simple crop recommendation API endpoint
    """
    print("\nTesting simple crop recommendation API...")
    url = "http://localhost:8000/api/simple-recommend/"
    
    payload = {
        "address": "Nairobi, Kenya"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success!")
            data = response.json()
            print("Recommendations:")
            for crop, details in data["recommendations"].items():
                print(f"- {crop}: Score {details['score']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_crop_recommendation_api()
    test_simple_crop_recommendation_api()
