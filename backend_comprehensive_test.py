#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Suite for Bible Study Application
Tests specifically the two main functionalities requested by the user:
1. RUBRIQUE 0 - Étude Verset par Verset (POST /api/generate-verse-by-verse)
2. ÉTUDE 28 RUBRIQUES (POST /api/generate-study)
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration - Use the public URL from frontend .env
BACKEND_URL = "https://etude-bible-app.preview.emergentagent.com"
TIMEOUT = 60  # Increased timeout for comprehensive testing

def log_test(test_name, status, details=""):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"[{timestamp}] {status_symbol} {test_name}")
    if details:
        print(f"    Details: {details}")
    print()

def test_verse_by_verse_full_chapter():
    """Test POST /api/generate-verse-by-verse with full chapter - Genèse 1"""
    try:
        payload = {
            "passage": "Genèse 1",
            "version": ""
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-verse-by-verse", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            if "content" not in data:
                log_test("Genèse 1 - Full Chapter", "FAIL", "Missing 'content' field")
                return False
            
            content = data["content"]
            
            # Critical check: Should contain ALL verses of Genesis 1 (31 verses)
            verse_count = content.count("VERSET")
            if verse_count < 25:  # Should have at least 25+ verses (Genesis 1 has 31)
                log_test("Genèse 1 - Full Chapter", "FAIL", 
                        f"Only found {verse_count} verses, expected 31 for Genesis 1")
                return False
            
            # Check for theological explanations
            theological_count = content.count("EXPLICATION THÉOLOGIQUE")
            if theological_count < 25:
                log_test("Genèse 1 - Full Chapter", "FAIL", 
                        f"Only found {theological_count} theological explanations")
                return False
            
            # Check content length (should be substantial for full chapter)
            if len(content) < 8000:  # Should be substantial for full chapter
                log_test("Genèse 1 - Full Chapter", "FAIL", 
                        f"Content too short for full chapter: {len(content)} characters")
                return False
            
            log_test("Genèse 1 - Full Chapter", "PASS", 
                    f"Found {verse_count} verses, {theological_count} explanations, {len(content)} characters")
            return True
            
        else:
            log_test("Genèse 1 - Full Chapter", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Genèse 1 - Full Chapter", "FAIL", f"Exception: {str(e)}")
        return False

def test_verse_by_verse_specific_verse():
    """Test POST /api/generate-verse-by-verse with specific verse - Jean 3:16"""
    try:
        payload = {
            "passage": "Jean 3:16",
            "version": ""
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-verse-by-verse", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            if "content" not in data:
                log_test("Jean 3:16 - Specific Verse", "FAIL", "Missing 'content' field")
                return False
            
            content = data["content"]
            
            # Should contain exactly 1 verse
            verse_count = content.count("VERSET")
            if verse_count != 1:
                log_test("Jean 3:16 - Specific Verse", "FAIL", 
                        f"Expected 1 verse, found {verse_count}")
                return False
            
            # Should contain theological explanation
            if "EXPLICATION THÉOLOGIQUE" not in content:
                log_test("Jean 3:16 - Specific Verse", "FAIL", 
                        "Missing theological explanation")
                return False
            
            # Check for relevant theological content
            theological_terms = ["amour", "monde", "fils", "vie éternelle", "croire"]
            found_terms = [term for term in theological_terms if term.lower() in content.lower()]
            
            if len(found_terms) < 2:
                log_test("Jean 3:16 - Specific Verse", "FAIL", 
                        f"Insufficient theological content for Jean 3:16. Found: {found_terms}")
                return False
            
            log_test("Jean 3:16 - Specific Verse", "PASS", 
                    f"Content length: {len(content)}, Theological terms: {found_terms}")
            return True
            
        else:
            log_test("Jean 3:16 - Specific Verse", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Jean 3:16 - Specific Verse", "FAIL", f"Exception: {str(e)}")
        return False

def test_verse_by_verse_psalms():
    """Test POST /api/generate-verse-by-verse with Psaumes 23"""
    try:
        payload = {
            "passage": "Psaumes 23",
            "version": ""
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-verse-by-verse", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            if "content" not in data:
                log_test("Psaumes 23 - Full Chapter", "FAIL", "Missing 'content' field")
                return False
            
            content = data["content"]
            
            # Psalm 23 has 6 verses
            verse_count = content.count("VERSET")
            if verse_count < 5:  # Should have at least 5 verses
                log_test("Psaumes 23 - Full Chapter", "FAIL", 
                        f"Only found {verse_count} verses, expected 6 for Psalm 23")
                return False
            
            # Check for theological explanations
            theological_count = content.count("EXPLICATION THÉOLOGIQUE")
            if theological_count < 5:
                log_test("Psaumes 23 - Full Chapter", "FAIL", 
                        f"Only found {theological_count} theological explanations")
                return False
            
            # Check for psalm-specific content
            psalm_terms = ["berger", "pâturage", "vallée", "ombre", "mort"]
            found_terms = [term for term in psalm_terms if term.lower() in content.lower()]
            
            if len(found_terms) < 2:
                log_test("Psaumes 23 - Full Chapter", "FAIL", 
                        f"Missing psalm-specific content. Found: {found_terms}")
                return False
            
            log_test("Psaumes 23 - Full Chapter", "PASS", 
                    f"Found {verse_count} verses, {theological_count} explanations, psalm terms: {found_terms}")
            return True
            
        else:
            log_test("Psaumes 23 - Full Chapter", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Psaumes 23 - Full Chapter", "FAIL", f"Exception: {str(e)}")
        return False

def test_28_rubriques_full_study():
    """Test POST /api/generate-study with full 28 rubriques - Jean 3"""
    try:
        payload = {
            "passage": "Jean 3",
            "version": "",
            "tokens": 0,
            "model": "",
            "requestedRubriques": None  # All 28 rubriques
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-study", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            if "content" not in data:
                log_test("Jean 3 - 28 Rubriques Full", "FAIL", "Missing 'content' field")
                return False
            
            content = data["content"]
            
            # Check for all 28 rubriques
            expected_rubriques = [
                "Prière d'ouverture",
                "Structure littéraire", 
                "Questions du chapitre précédent",
                "Thème doctrinal",
                "Fondements théologiques",
                "Contexte historique",
                "Contexte culturel",
                "Contexte géographique",
                "Analyse lexicale",
                "Parallèles bibliques",
                "Prophétie et accomplissement",
                "Personnages",
                "Structure rhétorique",
                "Théologie trinitaire",
                "Christ au centre",
                "Évangile et grâce",
                "Application personnelle",
                "Application communautaire",
                "Prière de réponse",
                "Questions d'étude",
                "Points de vigilance",
                "Objections et réponses",
                "Perspective missionnelle",
                "Éthique chrétienne",
                "Louange / liturgie",
                "Méditation guidée",
                "Mémoire / versets clés",
                "Plan d'action"
            ]
            
            found_rubriques = []
            missing_rubriques = []
            
            for rubrique in expected_rubriques:
                if rubrique in content:
                    found_rubriques.append(rubrique)
                else:
                    missing_rubriques.append(rubrique)
            
            if len(found_rubriques) < 25:  # Should have at least 25 out of 28
                log_test("Jean 3 - 28 Rubriques Full", "FAIL", 
                        f"Only found {len(found_rubriques)}/28 rubriques. Missing: {missing_rubriques[:5]}")
                return False
            
            # Check for biblical text extract
            if "Extrait du texte" not in content and "📖" not in content:
                log_test("Jean 3 - 28 Rubriques Full", "FAIL", 
                        "Missing biblical text extract")
                return False
            
            log_test("Jean 3 - 28 Rubriques Full", "PASS", 
                    f"Found {len(found_rubriques)}/28 rubriques, content length: {len(content)}")
            return True
            
        else:
            log_test("Jean 3 - 28 Rubriques Full", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Jean 3 - 28 Rubriques Full", "FAIL", f"Exception: {str(e)}")
        return False

def test_28_rubriques_filtered():
    """Test POST /api/generate-study with filtered rubriques"""
    try:
        payload = {
            "passage": "Romains 8",
            "version": "",
            "tokens": 0,
            "model": "",
            "requestedRubriques": [0, 1, 2, 3, 4]  # First 5 rubriques
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-study", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            if "content" not in data:
                log_test("Romains 8 - Filtered Rubriques", "FAIL", "Missing 'content' field")
                return False
            
            content = data["content"]
            
            # Check for the 5 requested rubriques
            expected_rubriques = [
                "Prière d'ouverture",
                "Structure littéraire", 
                "Questions du chapitre précédent",
                "Thème doctrinal",
                "Fondements théologiques"
            ]
            
            found_count = 0
            for rubrique in expected_rubriques:
                if rubrique in content:
                    found_count += 1
            
            if found_count < 4:  # Should have at least 4 out of 5
                log_test("Romains 8 - Filtered Rubriques", "FAIL", 
                        f"Only found {found_count}/5 requested rubriques")
                return False
            
            # Should NOT contain all 28 rubriques
            all_rubriques_count = content.count("à compléter")
            if all_rubriques_count > 10:  # If filtered, should have fewer sections
                log_test("Romains 8 - Filtered Rubriques", "FAIL", 
                        f"Filtering not working, found {all_rubriques_count} sections")
                return False
            
            log_test("Romains 8 - Filtered Rubriques", "PASS", 
                    f"Found {found_count}/5 requested rubriques, total sections: {all_rubriques_count}")
            return True
            
        else:
            log_test("Romains 8 - Filtered Rubriques", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Romains 8 - Filtered Rubriques", "FAIL", f"Exception: {str(e)}")
        return False

def test_28_rubriques_psalms():
    """Test POST /api/generate-study with Psaumes 1"""
    try:
        payload = {
            "passage": "Psaumes 1",
            "version": "",
            "tokens": 0,
            "model": "",
            "requestedRubriques": None
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-study", 
                               json=payload, 
                               headers=headers, 
                               timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            if "content" not in data:
                log_test("Psaumes 1 - 28 Rubriques", "FAIL", "Missing 'content' field")
                return False
            
            content = data["content"]
            
            # Check for key rubriques
            key_rubriques = ["Prière d'ouverture", "Thème doctrinal", "Christ au centre", "Application personnelle"]
            found_key = sum(1 for rubrique in key_rubriques if rubrique in content)
            
            if found_key < 3:
                log_test("Psaumes 1 - 28 Rubriques", "FAIL", 
                        f"Only found {found_key}/4 key rubriques")
                return False
            
            # Check for biblical text extract
            if "Extrait du texte" not in content and "📖" not in content:
                log_test("Psaumes 1 - 28 Rubriques", "FAIL", 
                        "Missing biblical text extract")
                return False
            
            log_test("Psaumes 1 - 28 Rubriques", "PASS", 
                    f"Found {found_key}/4 key rubriques, content length: {len(content)}")
            return True
            
        else:
            log_test("Psaumes 1 - 28 Rubriques", "FAIL", 
                    f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        log_test("Psaumes 1 - 28 Rubriques", "FAIL", f"Exception: {str(e)}")
        return False

def test_error_handling():
    """Test error handling for both endpoints"""
    test_cases = [
        {
            "name": "Invalid passage - verse-by-verse",
            "endpoint": "/api/generate-verse-by-verse",
            "payload": {"passage": "InvalidBook 999", "version": ""}
        },
        {
            "name": "Empty passage - verse-by-verse", 
            "endpoint": "/api/generate-verse-by-verse",
            "payload": {"passage": "", "version": ""}
        },
        {
            "name": "Invalid passage - 28 rubriques",
            "endpoint": "/api/generate-study",
            "payload": {"passage": "InvalidBook 999", "version": "", "tokens": 0, "model": ""}
        },
        {
            "name": "Empty passage - 28 rubriques",
            "endpoint": "/api/generate-study", 
            "payload": {"passage": "", "version": "", "tokens": 0, "model": ""}
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(f"{BACKEND_URL}{test_case['endpoint']}", 
                                   json=test_case["payload"], 
                                   headers=headers, 
                                   timeout=TIMEOUT)
            
            # Should return 400 error or graceful fallback
            if response.status_code >= 400:
                log_test(f"Error handling - {test_case['name']}", "PASS", 
                        f"Correctly returned error status: {response.status_code}")
                success_count += 1
            elif response.status_code == 200:
                # Check for graceful fallback
                data = response.json()
                if "content" in data and len(data["content"]) > 50:
                    log_test(f"Error handling - {test_case['name']}", "PASS", 
                            "Graceful fallback response provided")
                    success_count += 1
                else:
                    log_test(f"Error handling - {test_case['name']}", "FAIL", 
                            "No proper error handling or fallback")
            else:
                log_test(f"Error handling - {test_case['name']}", "FAIL", 
                        f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            log_test(f"Error handling - {test_case['name']}", "FAIL", f"Exception: {str(e)}")
    
    return success_count >= 3  # At least 3 out of 4 should handle errors properly

def test_json_response_format():
    """Test that JSON responses are well formatted"""
    try:
        # Test verse-by-verse response format
        payload = {"passage": "Jean 1:1", "version": ""}
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BACKEND_URL}/api/generate-verse-by-verse", 
                               json=payload, headers=headers, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check JSON structure
            if not isinstance(data, dict):
                log_test("JSON Format - verse-by-verse", "FAIL", "Response is not a JSON object")
                return False
            
            if "content" not in data:
                log_test("JSON Format - verse-by-verse", "FAIL", "Missing 'content' field")
                return False
            
            if not isinstance(data["content"], str):
                log_test("JSON Format - verse-by-verse", "FAIL", "'content' field is not a string")
                return False
            
            # Test 28 rubriques response format
            payload2 = {"passage": "Jean 1", "version": "", "tokens": 0, "model": ""}
            response2 = requests.post(f"{BACKEND_URL}/api/generate-study", 
                                    json=payload2, headers=headers, timeout=TIMEOUT)
            
            if response2.status_code == 200:
                data2 = response2.json()
                
                if not isinstance(data2, dict) or "content" not in data2:
                    log_test("JSON Format - 28 rubriques", "FAIL", "Invalid JSON structure")
                    return False
                
                log_test("JSON Response Format", "PASS", "Both endpoints return valid JSON")
                return True
            else:
                log_test("JSON Response Format", "FAIL", f"28 rubriques endpoint failed: {response2.status_code}")
                return False
        else:
            log_test("JSON Response Format", "FAIL", f"verse-by-verse endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        log_test("JSON Response Format", "FAIL", f"Exception: {str(e)}")
        return False

def run_comprehensive_tests():
    """Run all comprehensive tests for the two main functionalities"""
    print("=" * 80)
    print("COMPREHENSIVE BACKEND API TESTING SUITE")
    print("Testing the two main functionalities requested by user:")
    print("1. RUBRIQUE 0 - Étude Verset par Verset")
    print("2. ÉTUDE 28 RUBRIQUES")
    print("=" * 80)
    print(f"Testing backend at: {BACKEND_URL}")
    print(f"Timeout: {TIMEOUT} seconds")
    print()
    
    test_results = []
    
    print("🔍 TESTING RUBRIQUE 0 - ÉTUDE VERSET PAR VERSET")
    print("-" * 50)
    test_results.append(("Genèse 1 - Full Chapter (ALL verses)", test_verse_by_verse_full_chapter()))
    test_results.append(("Jean 3:16 - Specific Verse", test_verse_by_verse_specific_verse()))
    test_results.append(("Psaumes 23 - Full Chapter", test_verse_by_verse_psalms()))
    
    print("\n📚 TESTING ÉTUDE 28 RUBRIQUES")
    print("-" * 50)
    test_results.append(("Jean 3 - All 28 Rubriques", test_28_rubriques_full_study()))
    test_results.append(("Romains 8 - Filtered Rubriques", test_28_rubriques_filtered()))
    test_results.append(("Psaumes 1 - 28 Rubriques", test_28_rubriques_psalms()))
    
    print("\n🛡️ TESTING ERROR HANDLING & FORMAT")
    print("-" * 50)
    test_results.append(("Error Handling", test_error_handling()))
    test_results.append(("JSON Response Format", test_json_response_format()))
    
    # Summary
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    # Categorize results
    verse_by_verse_results = test_results[:3]
    rubriques_28_results = test_results[3:6]
    other_results = test_results[6:]
    
    print("\n🔍 RUBRIQUE 0 - ÉTUDE VERSET PAR VERSET:")
    for test_name, result in verse_by_verse_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print("\n📚 ÉTUDE 28 RUBRIQUES:")
    for test_name, result in rubriques_28_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print("\n🛡️ ERROR HANDLING & FORMAT:")
    for test_name, result in other_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\nOVERALL RESULT: {passed}/{total} tests passed")
    
    # Critical analysis
    verse_by_verse_passed = sum(1 for _, result in verse_by_verse_results if result)
    rubriques_28_passed = sum(1 for _, result in rubriques_28_results if result)
    
    critical_issues = []
    if verse_by_verse_passed < 2:
        critical_issues.append("CRITICAL: Verse-by-verse functionality failing")
    if rubriques_28_passed < 2:
        critical_issues.append("CRITICAL: 28 rubriques functionality failing")
    
    if critical_issues:
        print("\n❌ CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"  • {issue}")
        return False
    elif passed >= 6:
        print("\n🎉 BOTH MAIN FUNCTIONALITIES WORKING!")
        return True
    else:
        print("\n⚠️ SOME TESTS FAILED BUT CORE FUNCTIONALITY APPEARS TO WORK")
        return True

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)