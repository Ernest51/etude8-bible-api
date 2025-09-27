#!/usr/bin/env python3
"""
Backend API Testing Suite for Bible Study Application - CORS Proxy Fix Testing
Tests the new proxy endpoints that were added to fix CORS issues
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration - Use the local backend URL
BACKEND_URL = "http://localhost:8001"
TIMEOUT = 120  # Increased timeout for proxy calls

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

def test_health_endpoint():
    """Test GET /api/health endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if "status" in data and data["status"] == "ok":
                log_test("GET /api/health - Health check", "PASS", f"Response: {data}")
                return True
            else:
                log_test("GET /api/health - Health check", "FAIL", f"Unexpected response: {data}")
                return False
        else:
            log_test("GET /api/health - Health check", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("GET /api/health - Health check", "FAIL", f"Exception: {str(e)}")
        return False

def test_proxy_verse_by_verse_jean3():
    """Test POST /api/proxy-verse-by-verse endpoint with Jean 3 (CRITICAL TEST)"""
    try:
        payload = {
            "passage": "Jean 3",
            "version": "LSG"
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/proxy-verse-by-verse", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            if "content" not in data:
                log_test("POST /api/proxy-verse-by-verse - Jean 3 (CRITICAL)", "FAIL", "Missing 'content' field")
                return False
            
            content = data["content"]
            
            # Check content length (should be substantial for verse-by-verse)
            if len(content) < 500:
                log_test("POST /api/proxy-verse-by-verse - Jean 3 (CRITICAL)", "FAIL", 
                        f"Content too short: {len(content)} characters")
                return False
            
            # Check for verse-by-verse structure
            verse_indicators = ["VERSET", "TEXTE BIBLIQUE", "EXPLICATION THÉOLOGIQUE"]
            found_indicators = [ind for ind in verse_indicators if ind in content]
            
            if len(found_indicators) < 2:
                log_test("POST /api/proxy-verse-by-verse - Jean 3 (CRITICAL)", "FAIL", 
                        f"Missing verse structure. Found: {found_indicators}")
                return False
            
            log_test("POST /api/proxy-verse-by-verse - Jean 3 (CRITICAL)", "PASS", 
                    f"Content length: {len(content)} characters, Structure: {found_indicators}")
            return True
            
        else:
            log_test("POST /api/proxy-verse-by-verse - Jean 3 (CRITICAL)", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("POST /api/proxy-verse-by-verse - Jean 3 (CRITICAL)", "FAIL", f"Exception: {str(e)}")
        return False

def test_proxy_28_study_jean3():
    """Test POST /api/proxy-28-study endpoint with Jean 3 rubrique 1"""
    try:
        payload = {
            "passage": "Jean 3",
            "version": "LSG",
            "tokens": 500,
            "model": "local",
            "requestedRubriques": [0]  # Rubrique 1 - Prière d'ouverture
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/proxy-28-study", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            if "content" not in data:
                log_test("POST /api/proxy-28-study - Jean 3 Rubrique 1", "FAIL", "Missing 'content' field")
                return False
            
            content = data["content"]
            
            # Check content length
            if len(content) < 100:
                log_test("POST /api/proxy-28-study - Jean 3 Rubrique 1", "FAIL", 
                        f"Content too short: {len(content)} characters")
                return False
            
            log_test("POST /api/proxy-28-study - Jean 3 Rubrique 1", "PASS", 
                    f"Content length: {len(content)} characters")
            return True
            
        else:
            log_test("POST /api/proxy-28-study - Jean 3 Rubrique 1", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("POST /api/proxy-28-study - Jean 3 Rubrique 1", "FAIL", f"Exception: {str(e)}")
        return False

def test_local_verse_by_verse():
    """Test local POST /api/generate-verse-by-verse endpoint (for comparison)"""
    try:
        payload = {
            "passage": "Jean 3",
            "version": "LSG"
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-verse-by-verse", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            if "content" not in data:
                log_test("POST /api/generate-verse-by-verse - Jean 3 (Local)", "FAIL", "Missing 'content' field")
                return False
            
            content = data["content"]
            
            if len(content) < 500:
                log_test("POST /api/generate-verse-by-verse - Jean 3 (Local)", "FAIL", 
                        f"Content too short: {len(content)} characters")
                return False
            
            log_test("POST /api/generate-verse-by-verse - Jean 3 (Local)", "PASS", 
                    f"Content length: {len(content)} characters")
            return True
            
        else:
            log_test("POST /api/generate-verse-by-verse - Jean 3 (Local)", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("POST /api/generate-verse-by-verse - Jean 3 (Local)", "FAIL", f"Exception: {str(e)}")
        return False

def test_local_28_study():
    """Test local POST /api/generate-study endpoint (for comparison)"""
    try:
        payload = {
            "passage": "Jean 3",
            "version": "LSG",
            "tokens": 500,
            "model": "local",
            "requestedRubriques": [0]
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-study", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if "content" in data and len(data["content"]) > 100:
                log_test("POST /api/generate-study - Jean 3 (Local)", "PASS", 
                        f"Content length: {len(data['content'])}")
                return True
            else:
                log_test("POST /api/generate-study - Jean 3 (Local)", "FAIL", 
                        "Invalid or insufficient content")
                return False
        else:
            log_test("POST /api/generate-study - Jean 3 (Local)", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("POST /api/generate-study - Jean 3 (Local)", "FAIL", f"Exception: {str(e)}")
        return False

def run_cors_proxy_tests():
    """Run all CORS proxy tests"""
    print("=" * 80)
    print("BACKEND API TESTING SUITE - CORS PROXY FIX")
    print("=" * 80)
    print(f"Testing backend at: {BACKEND_URL}")
    print(f"Timeout: {TIMEOUT} seconds")
    print()
    
    test_results = []
    
    # Test basic connectivity
    print("🔍 Testing basic connectivity...")
    test_results.append(("Root endpoint", test_root_endpoint()))
    test_results.append(("Health check", test_health_endpoint()))
    
    print("\n🎯 Testing CRITICAL CORS proxy endpoints...")
    # Test the critical proxy endpoints that fix CORS
    test_results.append(("PROXY verse-by-verse Jean 3 (CRITICAL)", test_proxy_verse_by_verse_jean3()))
    test_results.append(("PROXY 28-study Jean 3 Rubrique 1", test_proxy_28_study_jean3()))
    
    print("\n📋 Testing local endpoints (for comparison)...")
    test_results.append(("LOCAL verse-by-verse Jean 3", test_local_verse_by_verse()))
    test_results.append(("LOCAL 28-study Jean 3", test_local_28_study()))
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    critical_tests = [
        ("Root endpoint", test_results[0][1]),
        ("PROXY verse-by-verse Jean 3 (CRITICAL)", test_results[2][1])
    ]
    critical_passed = sum(1 for _, result in critical_tests if result)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        critical_marker = " [CRITICAL]" if "CRITICAL" in test_name else ""
        print(f"{status} - {test_name}{critical_marker}")
    
    print()
    print(f"OVERALL RESULT: {passed}/{total} tests passed")
    print(f"CRITICAL TESTS: {critical_passed}/{len(critical_tests)} passed")
    
    if critical_passed == len(critical_tests):
        print("🎉 CRITICAL CORS PROXY TESTS PASSED!")
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  Some non-critical tests failed but CORS fix is working")
        return True
    else:
        print("❌ CRITICAL CORS PROXY TESTS FAILED")
        return False

if __name__ == "__main__":
    success = run_cors_proxy_tests()
    sys.exit(0 if success else 1)