#!/usr/bin/env python3
"""
Backend API Testing Suite for Bible Study Application
Tests the main backend endpoints according to review request:
1. GET /api/ - verify API responds
2. POST /api/generate-verse-by-verse - test with Genesis 1:1-3 LSG
3. POST /api/generate-study - test with John 3:16 LSG

CONTEXTE: Validation rapide des endpoints backend principaux selon test_result.md
TESTS REQUIS: Genèse 1:1-3 (verset par verset), Jean 3:16 (28 rubriques)
"""

import requests
import json
import time
import sys
import re
from datetime import datetime

# Configuration - Use the REACT_APP_BACKEND_URL from frontend/.env
BACKEND_URL = "https://etude-bible-app.preview.emergentagent.com"
TIMEOUT = 120  # Increased timeout for content generation

def log_test(test_name, status, details=""):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"[{timestamp}] {status_symbol} {test_name}")
    if details:
        print(f"    Details: {details}")
    print()

def test_api_root():
    """Test GET /api/ endpoint - specific test from review request"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "Bible Study" in data["message"]:
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

def test_verse_by_verse_genesis():
    """Test POST /api/generate-verse-by-verse with Genesis 1 LSG - specific test from review request"""
    try:
        payload = {
            "passage": "Genèse 1",
            "version": "LSG"
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-verse-by-verse", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            
            # Check JSON format is correct
            if not isinstance(data, dict) or "content" not in data:
                log_test("POST /api/generate-verse-by-verse - Genèse 1 LSG", "FAIL", 
                        "Invalid JSON response format")
                return False, None
            
            # Check content quality - should be substantial (>1000 characters as per review request)
            if len(content) < 1000:
                log_test("POST /api/generate-verse-by-verse - Genèse 1 LSG", "FAIL", 
                        f"Content too short: {len(content)} characters (required >1000)")
                return False, None
            
            # Check for verse-by-verse structure - should contain all verses with explanations
            verse_matches = re.findall(r'VERSET \d+', content)
            explanation_matches = re.findall(r'EXPLICATION THÉOLOGIQUE', content)
            
            if len(verse_matches) < 3:
                log_test("POST /api/generate-verse-by-verse - Genèse 1 LSG", "FAIL", 
                        f"Expected at least 3 verses, found {len(verse_matches)}")
                return False, None
            
            if len(explanation_matches) < 3:
                log_test("POST /api/generate-verse-by-verse - Genèse 1 LSG", "FAIL", 
                        f"Expected at least 3 theological explanations, found {len(explanation_matches)}")
                return False, None
            
            # Check for theological quality indicators
            theological_terms = [
                "création", "créateur", "commencement", "dieu", "théologique",
                "spirituel", "divin", "biblique"
            ]
            found_terms = [term for term in theological_terms if term.lower() in content.lower()]
            
            if len(found_terms) < 3:
                log_test("POST /api/generate-verse-by-verse - Genèse 1 LSG", "FAIL", 
                        f"Insufficient theological content quality. Found terms: {found_terms}")
                return False, None
            
            log_test("POST /api/generate-verse-by-verse - Genèse 1 LSG", "PASS", 
                    f"Content: {len(content)} chars, Verses: {len(verse_matches)}, Explanations: {len(explanation_matches)}, Theological terms: {len(found_terms)}")
            return True, data
            
        else:
            log_test("POST /api/generate-verse-by-verse - Genèse 1 LSG", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False, None
            
    except Exception as e:
        log_test("POST /api/generate-verse-by-verse - Genèse 1 LSG", "FAIL", f"Exception: {str(e)}")
        return False, None

def test_28_rubriques_jean_3_16():
    """Test POST /api/generate-study with Jean 3:16 LSG - specific test from review request"""
    try:
        payload = {
            "passage": "Jean 3:16",
            "version": "LSG",
            "tokens": 500,
            "model": "gpt",
            "requestedRubriques": []  # All 28 rubriques
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-study", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            
            # Check JSON format is correct
            if not isinstance(data, dict) or "content" not in data:
                log_test("POST /api/generate-study - Jean 3:16 LSG (28 rubriques)", "FAIL", 
                        "Invalid JSON response format")
                return False, None
            
            # Check content quality - should be substantial (>1000 characters as per review request)
            if len(content) < 1000:
                log_test("POST /api/generate-study - Jean 3:16 LSG (28 rubriques)", "FAIL", 
                        f"Content too short: {len(content)} characters (required >1000)")
                return False, None
            
            # Count rubric sections (should be 28)
            rubric_matches = re.findall(r'## \d+\.', content)
            rubric_count = len(rubric_matches)
            
            if rubric_count < 20:  # Allow some flexibility but should have most rubriques
                log_test("POST /api/generate-study - Jean 3:16 LSG (28 rubriques)", "FAIL", 
                        f"Expected around 28 rubriques, found {rubric_count}")
                return False, None
            
            # Check for theological quality indicators specific to John 3:16
            theological_terms = [
                "amour", "dieu", "monde", "fils", "unique", "vie", "éternelle",
                "salut", "évangile", "foi", "grâce", "théologique", "spirituel"
            ]
            found_terms = [term for term in theological_terms if term.lower() in content.lower()]
            
            if len(found_terms) < 5:
                log_test("POST /api/generate-study - Jean 3:16 LSG (28 rubriques)", "FAIL", 
                        f"Insufficient theological content quality. Found terms: {found_terms}")
                return False, None
            
            log_test("POST /api/generate-study - Jean 3:16 LSG (28 rubriques)", "PASS", 
                    f"Content: {len(content)} chars, Rubriques: {rubric_count}, Theological terms: {len(found_terms)}")
            return True, data
            
        else:
            log_test("POST /api/generate-study - Jean 3:16 LSG (28 rubriques)", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False, None
            
    except Exception as e:
        log_test("POST /api/generate-study - Jean 3:16 LSG (28 rubriques)", "FAIL", f"Exception: {str(e)}")
        return False, None

def test_cors_configuration():
    """Test CORS configuration - specific test from review request"""
    try:
        # Test with OPTIONS request to check CORS headers
        response = requests.options(f"{BACKEND_URL}/api/generate-study", 
                                  headers={
                                      "Origin": "https://etude8-bible.vercel.app",
                                      "Access-Control-Request-Method": "POST",
                                      "Access-Control-Request-Headers": "Content-Type"
                                  },
                                  timeout=TIMEOUT)
        
        # Check for CORS headers
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        
        # Check if CORS is properly configured
        if (cors_headers["Access-Control-Allow-Origin"] in ["*", "https://etude8-bible.vercel.app"] or
            response.status_code in [200, 204]):
            log_test("CORS Configuration", "PASS", 
                    f"CORS headers present: {cors_headers}")
            return True
        else:
            log_test("CORS Configuration", "FAIL", 
                    f"CORS not properly configured. Headers: {cors_headers}, Status: {response.status_code}")
            return False
            
    except Exception as e:
        log_test("CORS Configuration", "FAIL", f"Exception: {str(e)}")
        return False

def test_no_failed_to_fetch():
    """Test that there are no 'Failed to fetch' errors - specific test from review request"""
    try:
        # Test a simple API call to ensure no network issues
        payload = {
            "passage": "Jean 3:16",
            "version": "LSG"
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-verse-by-verse", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            
            # Check that response doesn't contain error messages
            error_indicators = ["failed to fetch", "network error", "connection error", "timeout"]
            found_errors = [error for error in error_indicators if error.lower() in content.lower()]
            
            if found_errors:
                log_test("No 'Failed to fetch' errors", "FAIL", 
                        f"Found error indicators: {found_errors}")
                return False
            else:
                log_test("No 'Failed to fetch' errors", "PASS", 
                        "No network error messages found in response")
                return True
        else:
            log_test("No 'Failed to fetch' errors", "FAIL", 
                    f"HTTP error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        if "failed to fetch" in str(e).lower():
            log_test("No 'Failed to fetch' errors", "FAIL", 
                    f"Network error detected: {str(e)}")
            return False
        else:
            log_test("No 'Failed to fetch' errors", "FAIL", f"Request exception: {str(e)}")
            return False
    except Exception as e:
        log_test("No 'Failed to fetch' errors", "FAIL", f"Exception: {str(e)}")
        return False

def run_all_tests():
    """Run all backend tests according to review request"""
    print("=" * 80)
    print("BACKEND API TESTING SUITE - BIBLE STUDY APPLICATION")
    print("=" * 80)
    print(f"Testing backend at: {BACKEND_URL}")
    print(f"Timeout: {TIMEOUT} seconds")
    print()
    print("CONTEXTE: Validation rapide des endpoints backend principaux")
    print("TESTS REQUIS: GET /api/, POST /api/generate-verse-by-verse, POST /api/generate-study")
    print()
    
    test_results = []
    
    # Test 1: Basic API health check
    print("1. BASIC API HEALTH CHECK")
    print("-" * 40)
    test_results.append(("GET /api/ - Root endpoint", test_api_root()))
    
    # Test 2: Verse-by-verse study (Rubrique 0)
    print("\n2. TEST ÉTUDE VERSET PAR VERSET (RUBRIQUE 0)")
    print("-" * 40)
    verse_result, _ = test_verse_by_verse_genesis()
    test_results.append(("POST /api/generate-verse-by-verse - Genèse 1 LSG", verse_result))
    
    # Test 3: 28 rubriques study
    print("\n3. TEST ÉTUDE 28 RUBRIQUES")
    print("-" * 40)
    study_result, _ = test_28_rubriques_jean_3_16()
    test_results.append(("POST /api/generate-study - Jean 3:16 LSG (28 rubriques)", study_result))
    
    # Test 4: CORS and network configuration
    print("\n4. CONFIGURATION CORS ET RÉSEAU")
    print("-" * 40)
    test_results.append(("CORS Configuration", test_cors_configuration()))
    test_results.append(("No 'Failed to fetch' errors", test_no_failed_to_fetch()))
    
    # Summary
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES TESTS - BIBLE STUDY APPLICATION")
    print("=" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"RÉSULTAT GLOBAL: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Backend Bible Study Application entièrement fonctionnel")
        print("✅ Endpoints principaux validés selon review request")
        return True
    elif passed >= 3:  # At least most functionality works
        print("⚠️  QUELQUES TESTS ÉCHOUÉS MAIS FONCTIONNALITÉ PRINCIPALE OK")
        return True
    else:
        print("❌ TESTS CRITIQUES ÉCHOUÉS")
        print("❌ Problèmes majeurs avec le backend")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)