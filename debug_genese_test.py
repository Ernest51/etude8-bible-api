#!/usr/bin/env python3
"""
Debug test for Genèse 1:1 LSG endpoint
"""

import requests
import json

BACKEND_URL = "https://etude-bible-app.preview.emergentagent.com"

def test_genese_detailed():
    """Test POST /api/generate-verse-by-verse with Genèse 1:1 LSG and show full response"""
    try:
        payload = {
            "passage": "Genèse 1:1 LSG",
            "version": "LSG"
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-verse-by-verse", 
                               json=payload, 
                               headers=headers, 
                               timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {data.keys()}")
            
            if "content" in data:
                content = data["content"]
                print(f"Content length: {len(content)}")
                print("=" * 80)
                print("FULL CONTENT:")
                print("=" * 80)
                print(content)
                print("=" * 80)
                
                # Check for verse count
                verse_count = content.count("VERSET")
                print(f"Number of verses found: {verse_count}")
                
                # Check for specific verse numbers
                for i in range(1, 32):  # Genèse 1 has 31 verses
                    if f"VERSET {i}" in content:
                        print(f"✅ Found VERSET {i}")
                    else:
                        print(f"❌ Missing VERSET {i}")
                        
            else:
                print("❌ No 'content' field in response")
                print(f"Response: {data}")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_genese_detailed()