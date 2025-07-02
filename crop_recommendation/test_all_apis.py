#!/usr/bin/env python3
import os
import sys
import json
import requests
from datetime import datetime

# Import test functions from other test files
from test_crop_api import test_crop_recommendation_api, test_simple_crop_recommendation_api
from test_disease_api import test_disease_detection_api

def check_api_health():
    """
    Simple health check for the API server
    """
    print("\n==== Performing API Health Check ====")
    try:
        # Try to reach the Django admin page as a basic check
        response = requests.get("http://localhost:8000/admin/")
        if response.status_code in [200, 302]:  # 302 is redirect to login
            print("✅ API server is running")
            return True
        else:
            print(f"⚠️ API server response code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not reachable - make sure the Docker container is running")
        return False

def test_auth_api():
    """
    Test the authentication API
    """
    print("\n==== Testing Authentication API ====")
    url = "http://localhost:8000/api/auth/register/"
    
    # Generate a unique username using timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    username = f"testuser_{timestamp}"
    
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Registration Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ User registration successful")
            data = response.json()
            token = data.get("token")
            if token:
                print(f"✅ Authentication token received")
                return True
            else:
                print("⚠️ No authentication token in response")
        else:
            print(f"⚠️ Registration error: {response.text}")
        
        return False
    except Exception as e:
        print(f"❌ Error testing auth API: {str(e)}")
        return False

def test_marketplace_api():
    """
    Test the marketplace API endpoints
    """
    print("\n==== Testing Marketplace API ====")
    url = "http://localhost:8000/api/marketplace/items/"
    
    try:
        response = requests.get(url)
        print(f"Marketplace Items Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            item_count = len(data)
            print(f"✅ Retrieved {item_count} marketplace items")
            return True
        else:
            print(f"⚠️ Marketplace API error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing marketplace API: {str(e)}")
        return False

def run_all_tests():
    """
    Run all API tests and collect results
    """
    print("="*50)
    print("RUNNING COMPREHENSIVE API TESTS")
    print("="*50)
    
    results = {}
    
    # Check if API is up
    if not check_api_health():
        print("\n❌ API server is not responding - tests aborted")
        return
    
    # Run all tests
    try:
        print("\n==== Testing Crop Recommendation API ====")
        test_crop_recommendation_api()
        test_simple_crop_recommendation_api()
        
        print("\n==== Testing Disease Detection API ====")
        test_disease_detection_api()
        
        # Test authentication API
        test_auth_api()
        
        # Test marketplace API
        test_marketplace_api()
        
        print("\n==== All Tests Completed ====")
        
    except Exception as e:
        print(f"\n❌ Error during test execution: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
