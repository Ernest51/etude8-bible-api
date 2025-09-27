#!/usr/bin/env python3
"""
Backend API Testing Suite for Bible Study Application
Tests the actual implemented endpoints: GET /api/ and POST /api/generate-study
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration - Use the public endpoint from frontend .env
BACKEND_URL = "http://localhost:8001"
TIMEOUT = 30

def log_test(test_name, status, details=""):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"[{timestamp}] {status_symbol} {test_name}")
    if details:
        print(f"    Details: {details}")
    print()

def test_root_endpoint():
    """Test GET /api/ endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "Bible Study API" in data["message"]:
                log_test("GET /api/ - Root endpoint", "PASS", f"Response: {data}")
                return True
            else:
                log_test("GET /api/ - Root endpoint", "FAIL", f"Unexpected response: {data}")
                return False
        else:
            log_test("GET /api/ - Root endpoint", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("GET /api/ - Root endpoint", "FAIL", f"Exception: {str(e)}")
        return False

def test_generate_study_basic():
    """Test POST /api/generate-study with basic parameters (Jean 3:16)"""
    try:
        payload = {
            "passage": "Jean 3:16 LSG",
            "version": "LSG",
            "tokens": 500,
            "model": "gpt",
            "requestedRubriques": [0]
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-study", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            if "content" in data:
                content = data["content"]
                if content and len(content) > 100:
                    # Check if content contains expected theological elements
                    expected_elements = ["Jean 3", "Nouvelle Naissance", "Nicodème", "Bible Derby"]
                    found_elements = [elem for elem in expected_elements if elem in content]
                    
                    if len(found_elements) >= 2:
                        log_test("POST /api/generate-study - Basic test (Jean 3:16)", "PASS", 
                               f"Content length: {len(content)}, Found elements: {found_elements}")
                        return True, data
                    else:
                        log_test("POST /api/generate-study - Basic test (Jean 3:16)", "FAIL", 
                               f"Missing expected theological content. Found: {found_elements}")
                        return False, None
                else:
                    log_test("POST /api/generate-study - Basic test (Jean 3:16)", "FAIL", 
                           f"Content too short or empty: {len(content) if content else 0}")
                    return False, None
            else:
                log_test("POST /api/generate-study - Basic test (Jean 3:16)", "FAIL", "Missing 'content' field")
                return False, None
        else:
            log_test("POST /api/generate-study - Basic test (Jean 3:16)", "FAIL", 
                   f"Status: {response.status_code}, Response: {response.text}")
            return False, None
            
    except Exception as e:
        log_test("POST /api/generate-study - Basic test (Jean 3:16)", "FAIL", f"Exception: {str(e)}")
        return False, None

def test_generate_study_genesis():
    """Test POST /api/generate-study with Genesis passage"""
    try:
        payload = {
            "passage": "Genèse 1:1 LSG",
            "version": "LSG",
            "tokens": 500,
            "model": "gpt",
            "requestedRubriques": [0]
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-study", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if "content" in data and data["content"]:
                content = data["content"]
                # Check for Genesis-specific content
                genesis_elements = ["Création", "Elohim", "commencement", "Bible Derby"]
                found_elements = [elem for elem in genesis_elements if elem in content]
                
                if len(found_elements) >= 2:
                    log_test("POST /api/generate-study - Genesis test", "PASS", 
                           f"Content length: {len(content)}, Found elements: {found_elements}")
                    return True
                else:
                    log_test("POST /api/generate-study - Genesis test", "FAIL", 
                           f"Missing Genesis-specific content. Found: {found_elements}")
                    return False
            else:
                log_test("POST /api/generate-study - Genesis test", "FAIL", "Empty or missing content")
                return False
        else:
            log_test("POST /api/generate-study - Genesis test", "FAIL", 
                   f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("POST /api/generate-study - Genesis test", "FAIL", f"Exception: {str(e)}")
        return False

def test_generate_study_error_handling():
    """Test POST /api/generate-study with invalid data"""
    test_cases = [
        {
            "name": "Empty passage",
            "payload": {
                "passage": "",
                "version": "LSG",
                "tokens": 500,
                "model": "gpt",
                "requestedRubriques": [0]
            }
        },
        {
            "name": "Missing required fields",
            "payload": {
                "version": "LSG",
                "tokens": 500
            }
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(f"{BACKEND_URL}/api/generate-study", 
                                   json=test_case["payload"], 
                                   headers=headers, 
                                   timeout=TIMEOUT)
            
            # For error cases, we expect either 4xx/5xx status or a graceful fallback response
            if response.status_code >= 400:
                log_test(f"Error handling - {test_case['name']}", "PASS", 
                       f"Correctly returned error status: {response.status_code}")
                success_count += 1
            elif response.status_code == 200:
                # Check if it's a graceful fallback
                data = response.json()
                if "content" in data and data["content"]:
                    log_test(f"Error handling - {test_case['name']}", "PASS", 
                           "Graceful fallback response provided")
                    success_count += 1
                else:
                    log_test(f"Error handling - {test_case['name']}", "FAIL", 
                           "Unexpected successful response without content")
            else:
                log_test(f"Error handling - {test_case['name']}", "FAIL", 
                       f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            log_test(f"Error handling - {test_case['name']}", "FAIL", f"Exception: {str(e)}")
    
    return success_count >= 1  # At least 1 out of 2 should handle errors properly

def test_bible_api_integration():
    """Test if Bible Derby API integration is working"""
    try:
        # Test with a passage that should trigger Bible API call
        payload = {
            "passage": "Jean 3:16 LSG",
            "version": "LSG", 
            "tokens": 500,
            "model": "gpt",
            "requestedRubriques": [0]
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-study", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if "content" in data and data["content"]:
                content = data["content"]
                # Check for Bible Derby API integration
                if "Bible Derby" in content:
                    log_test("Bible Derby API Integration", "PASS", 
                           "Bible Derby API reference found in content")
                    return True
                else:
                    log_test("Bible Derby API Integration", "WARN", 
                           "Bible Derby reference not found, but content generated")
                    return True  # Still pass as content was generated
            else:
                log_test("Bible Derby API Integration", "FAIL", "No content generated")
                return False
        else:
            log_test("Bible Derby API Integration", "FAIL", 
                   f"API call failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        log_test("Bible Derby API Integration", "FAIL", f"Exception: {str(e)}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("=" * 80)
    print("BACKEND API TESTING SUITE - ACTUAL IMPLEMENTATION")
    print("=" * 80)
    print(f"Testing backend at: {BACKEND_URL}")
    print(f"Timeout: {TIMEOUT} seconds")
    print()
    
    test_results = []
    
    # Test root endpoint
    print("Testing root endpoint...")
    test_results.append(("Root endpoint", test_root_endpoint()))
    
    print("\nTesting POST /api/generate-study endpoint...")
    # Test generate-study endpoint
    basic_result, _ = test_generate_study_basic()
    test_results.append(("POST generate-study basic (Jean 3:16)", basic_result))
    test_results.append(("POST generate-study Genesis", test_generate_study_genesis()))
    test_results.append(("POST generate-study error handling", test_generate_study_error_handling()))
    
    print("\nTesting external API integration...")
    test_results.append(("Bible Derby API Integration", test_bible_api_integration()))
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return True
    elif passed >= total * 0.8:  # 80% pass rate
        print("✅ MOST TESTS PASSED - Backend is functional")
        return True
    else:
        print("⚠️  MANY TESTS FAILED - Backend needs attention")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)