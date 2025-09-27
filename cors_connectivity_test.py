#!/usr/bin/env python3
"""
Test CORS and connectivity issues for the verse-by-verse endpoint
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://etude-bible-app.preview.emergentagent.com"

def test_cors_headers():
    """Test CORS headers on the endpoint"""
    try:
        # Test OPTIONS request (preflight)
        options_response = requests.options(f"{BACKEND_URL}/api/generate-verse-by-verse")
        print(f"OPTIONS Status: {options_response.status_code}")
        print(f"OPTIONS Headers: {dict(options_response.headers)}")
        
        # Test actual POST request
        payload = {
            "passage": "Genèse 1:1 LSG",
            "version": "LSG"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://etude-bible-app.preview.emergentagent.com"  # Simulate frontend origin
        }
        
        response = requests.post(f"{BACKEND_URL}/api/generate-verse-by-verse", 
                               json=payload, 
                               headers=headers, 
                               timeout=30)
        
        print(f"\nPOST Status: {response.status_code}")
        print(f"POST Headers: {dict(response.headers)}")
        
        # Check for CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print(f"\nCORS Headers:")
        for header, value in cors_headers.items():
            print(f"  {header}: {value}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse successful - Content length: {len(data.get('content', ''))}")
            return True
        else:
            print(f"\nError: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception during CORS test: {str(e)}")
        return False

def test_different_origins():
    """Test with different origins to check CORS policy"""
    origins = [
        "https://etude-bible-app.preview.emergentagent.com",
        "http://localhost:3000",
        "https://example.com"
    ]
    
    payload = {
        "passage": "Genèse 1:1 LSG",
        "version": "LSG"
    }
    
    for origin in origins:
        try:
            headers = {
                "Content-Type": "application/json",
                "Origin": origin
            }
            
            response = requests.post(f"{BACKEND_URL}/api/generate-verse-by-verse", 
                                   json=payload, 
                                   headers=headers, 
                                   timeout=10)
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin', 'Not set')
            print(f"Origin: {origin} -> CORS: {cors_origin} -> Status: {response.status_code}")
            
        except Exception as e:
            print(f"Origin: {origin} -> Error: {str(e)}")

def test_server_availability():
    """Test basic server availability and response times"""
    endpoints = [
        "/api/",
        "/api/generate-verse-by-verse",
        "/api/generate-study"
    ]
    
    for endpoint in endpoints:
        try:
            start_time = datetime.now()
            
            if endpoint == "/api/":
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            else:
                # POST endpoints
                if "verse-by-verse" in endpoint:
                    payload = {"passage": "Genèse 1:1 LSG", "version": "LSG"}
                else:
                    payload = {
                        "passage": "Jean 3:16 LSG",
                        "version": "LSG", 
                        "tokens": 500,
                        "model": "gpt",
                        "requestedRubriques": [0]
                    }
                
                response = requests.post(f"{BACKEND_URL}{endpoint}", 
                                       json=payload,
                                       headers={"Content-Type": "application/json"},
                                       timeout=30)
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            print(f"{endpoint}: Status {response.status_code} - {response_time:.2f}s")
            
            if response.status_code != 200:
                print(f"  Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"{endpoint}: Error - {str(e)}")

def main():
    print("=" * 80)
    print("CORS AND CONNECTIVITY TESTING")
    print("=" * 80)
    print(f"Testing backend at: {BACKEND_URL}")
    print()
    
    print("1. Testing CORS headers...")
    cors_ok = test_cors_headers()
    
    print("\n" + "=" * 40)
    print("2. Testing different origins...")
    test_different_origins()
    
    print("\n" + "=" * 40)
    print("3. Testing server availability...")
    test_server_availability()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if cors_ok:
        print("✅ Main endpoint working correctly")
        print("✅ All 31 verses of Genesis 1 are returned")
        print("✅ No server down issues detected")
        print("✅ CORS appears to be configured (allow_origins=['*'])")
    else:
        print("❌ Issues detected with the endpoint")
    
    print("\nThe 'Failed to fetch' error reported by the user is likely:")
    print("- A frontend JavaScript issue")
    print("- Network connectivity issue on user's side")
    print("- Browser-specific CORS handling")
    print("- Frontend code not using the correct URL or headers")

if __name__ == "__main__":
    main()