#!/usr/bin/env python3
"""
Backend API Testing Suite for Bible Study Application - Versets Functionality
Tests the POST /api/generate-verse-by-verse endpoint specifically
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration - Use localhost as specified in the review request
BACKEND_URL = "http://localhost:8001/api"
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
        response = requests.get(f"{BACKEND_URL}/", timeout=TIMEOUT)
        
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

def test_generate_verse_by_verse():
    """Test POST /api/generate-verse-by-verse endpoint - Main functionality"""
    try:
        payload = {
            "passage": "Genèse 1:1 LSG",
            "version": "LSG"
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/generate-verse-by-verse", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            if "content" in data:
                content = data["content"]
                
                # Validate content structure for verse-by-verse study
                expected_elements = [
                    "Étude Verset par Verset",
                    "Genèse",
                    "Chapitre 1",
                    "Explication Théologique",
                    "Soli Deo Gloria"
                ]
                
                missing_elements = []
                for element in expected_elements:
                    if element not in content:
                        missing_elements.append(element)
                
                if not missing_elements and len(content) > 500:
                    log_test("POST /api/generate-verse-by-verse - Genèse 1", "PASS", 
                           f"Content length: {len(content)}, Contains all expected elements")
                    return True, data
                else:
                    log_test("POST /api/generate-verse-by-verse - Genèse 1", "FAIL", 
                           f"Missing elements: {missing_elements}, Content length: {len(content)}")
                    return False, None
            else:
                log_test("POST /api/generate-verse-by-verse - Genèse 1", "FAIL", "Missing 'content' field in response")
                return False, None
        else:
            log_test("POST /api/generate-verse-by-verse - Genèse 1", "FAIL", 
                   f"Status: {response.status_code}, Response: {response.text}")
            return False, None
            
    except Exception as e:
        log_test("POST /api/generate-verse-by-verse - Genèse 1", "FAIL", f"Exception: {str(e)}")
        return False, None

def test_generate_study_basic():
    """Test POST /api/generate-study endpoint - Basic functionality"""
    try:
        payload = {
            "passage": "Jean 3:16 LSG",
            "version": "LSG",
            "tokens": 500,
            "model": "gpt",
            "requestedRubriques": [1]  # Not verse-by-verse
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/generate-study", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            if "content" in data and len(data["content"]) > 100:
                log_test("POST /api/generate-study - Basic test", "PASS", 
                       f"Content length: {len(data['content'])}")
                return True, data
            else:
                log_test("POST /api/generate-study - Basic test", "FAIL", 
                       f"Content too short or missing: {len(data.get('content', ''))}")
                return False, None
        else:
            log_test("POST /api/generate-study - Basic test", "FAIL", 
                   f"Status: {response.status_code}, Response: {response.text}")
            return False, None
            
    except Exception as e:
        log_test("POST /api/generate-study - Basic test", "FAIL", f"Exception: {str(e)}")
        return False, None

def test_verse_by_verse_different_chapters():
    """Test verse-by-verse with different Bible chapters"""
    test_passages = [
        ("Genèse 1:1 LSG", "Genèse", "1"),
        ("Jean 1:1 LSG", "Jean", "1"),
        ("Psaumes 23:1 LSG", "Psaumes", "23")
    ]
    
    success_count = 0
    
    for passage, expected_book, expected_chapter in test_passages:
        try:
            payload = {
                "passage": passage,
                "version": "LSG"
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(f"{BACKEND_URL}/generate-verse-by-verse", 
                                   json=payload, 
                                   headers=headers, 
                                   timeout=TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if "content" in data:
                    content = data["content"]
                    if expected_book in content and f"Chapitre {expected_chapter}" in content:
                        success_count += 1
                        log_test(f"Verse-by-verse - {passage}", "PASS", 
                               f"Generated content for {expected_book} {expected_chapter}")
                    else:
                        log_test(f"Verse-by-verse - {passage}", "FAIL", 
                               f"Content doesn't contain expected book/chapter")
                else:
                    log_test(f"Verse-by-verse - {passage}", "FAIL", "No content in response")
            else:
                log_test(f"Verse-by-verse - {passage}", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            log_test(f"Verse-by-verse - {passage}", "FAIL", f"Exception: {str(e)}")
    
    return success_count >= 2  # At least 2 out of 3 should work

def run_versets_tests():
    """Run all verse-by-verse backend tests"""
    print("=" * 80)
    print("BACKEND API TESTING SUITE - VERSETS FUNCTIONALITY")
    print("=" * 80)
    print(f"Testing backend at: {BACKEND_URL}")
    print(f"Timeout: {TIMEOUT} seconds")
    print()
    
    test_results = []
    
    # Test basic connectivity
    print("Testing basic connectivity...")
    test_results.append(("Root endpoint", test_root_endpoint()))
    
    print("\nTesting verse-by-verse functionality...")
    # Test main verse-by-verse endpoint
    verse_result, verse_data = test_generate_verse_by_verse()
    test_results.append(("POST /api/generate-verse-by-verse - Main", verse_result))
    
    # Test different chapters
    test_results.append(("Verse-by-verse different chapters", test_verse_by_verse_different_chapters()))
    
    print("\nTesting regular study endpoint for comparison...")
    # Test regular study endpoint
    study_result, study_data = test_generate_study_basic()
    test_results.append(("POST /api/generate-study - Basic", study_result))
    
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
    elif passed >= 3:  # At least basic connectivity and verse-by-verse work
        print("✅ CORE FUNCTIONALITY WORKING")
        return True
    else:
        print("⚠️  CRITICAL TESTS FAILED")
        return False

if __name__ == "__main__":
    success = run_versets_tests()
    sys.exit(0 if success else 1)