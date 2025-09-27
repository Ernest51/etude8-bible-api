#!/usr/bin/env python3
"""
Test script for Railway deployment of Bible Study API
Tests all endpoints including Gemini integration
"""

import requests
import json
import time
import sys

def test_endpoint(base_url, endpoint, method="GET", data=None, timeout=30):
    """Test a specific endpoint"""
    url = f"{base_url}{endpoint}"
    print(f"\n🔍 Testing {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if endpoint == "/api/health":
                print(f"   Gemini Available: {result.get('gemini_enabled', 'Unknown')}")
                print(f"   Intelligent Mode: {result.get('intelligent_mode', 'Unknown')}")
            elif "generate" in endpoint:
                content_length = len(result.get('content', ''))
                print(f"   Content Length: {content_length} chars")
                if content_length > 1000:
                    print(f"   ✅ Rich content generated")
                else:
                    print(f"   ⚠️  Content might be basic")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout after {timeout}s")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py <railway-url>")
        print("Example: python test_deployment.py https://your-app.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    print(f"🚀 Testing Railway deployment: {base_url}")
    
    # Test basic endpoints
    tests = [
        ("Health Check", "/api/health", "GET", None, 10),
        ("Root", "/api/", "GET", None, 10),
    ]
    
    # Test generation endpoints
    test_data = {"passage": "Jean 3:16", "version": "LSG"}
    generation_tests = [
        ("Standard Verse Generation", "/api/generate-verse-by-verse", "POST", test_data, 60),
        ("Gemini Verse Generation", "/api/generate-verse-by-verse-gemini", "POST", test_data, 120),
        ("Study Generation", "/api/generate-study", "POST", test_data, 60),
    ]
    
    # Run basic tests
    print("\n" + "="*50)
    print("BASIC ENDPOINT TESTS")
    print("="*50)
    
    basic_success = 0
    for name, endpoint, method, data, timeout in tests:
        if test_endpoint(base_url, endpoint, method, data, timeout):
            basic_success += 1
    
    # Run generation tests
    print("\n" + "="*50)
    print("GENERATION ENDPOINT TESTS")
    print("="*50)
    
    generation_success = 0
    for name, endpoint, method, data, timeout in generation_tests:
        if test_endpoint(base_url, endpoint, method, data, timeout):
            generation_success += 1
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Basic Tests: {basic_success}/{len(tests)} passed")
    print(f"Generation Tests: {generation_success}/{len(generation_tests)} passed")
    
    total_tests = len(tests) + len(generation_tests)
    total_success = basic_success + generation_success
    
    print(f"Overall: {total_success}/{total_tests} tests passed")
    
    if total_success == total_tests:
        print("🎉 All tests passed! Deployment is successful.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())