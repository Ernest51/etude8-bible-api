#!/usr/bin/env python3
"""
Test du système d'enrichissement automatique
"""

import sys
sys.path.append('/app/backend')

from verse_by_verse_content import get_verse_by_verse_content, get_all_verses_for_chapter
from server import generate_enriched_theological_explanation, generate_smart_fallback_explanation
import asyncio

def test_local_library():
    """Test la bibliothèque locale enrichie"""
    print("=== TEST BIBLIOTHÈQUE LOCALE ENRICHIE ===")
    
    # Test Genèse 1
    genese_1 = get_verse_by_verse_content("Genèse", 1)
    print(f"Genèse 1 contient {len(genese_1)} versets enrichis")
    
    if 1 in genese_1:
        verset_1 = genese_1[1]
        print(f"Genèse 1:1 - {verset_1['verse'][:50]}...")
        print(f"Explication: {verset_1['explanation'][:100]}...")
    
    # Test Jean 3:16
    jean_3 = get_verse_by_verse_content("Jean", 3)
    if 16 in jean_3:
        verset_16 = jean_3[16]
        print(f"\nJean 3:16 - {verset_16['verse']}")
        print(f"Explication: {verset_16['explanation'][:150]}...")
    
    # Test couverture des livres
    from verse_by_verse_content import VERSE_BY_VERSE_LIBRARY
    print(f"\nLivres couverts: {list(VERSE_BY_VERSE_LIBRARY.keys())}")
    
    total_versets = 0
    for livre, chapitres in VERSE_BY_VERSE_LIBRARY.items():
        for chapitre, versets in chapitres.items():
            total_versets += len(versets)
    
    print(f"Total versets enrichis dans la base: {total_versets}")

def test_smart_fallback():
    """Test le système de fallback intelligent"""
    print("\n=== TEST SYSTÈME DE FALLBACK INTELLIGENT ===")
    
    # Test différents types de versets
    test_cases = [
        ("Car Dieu a tant aimé le monde...", "Jean", 3, 16),
        ("Au commencement, Dieu créa les cieux et la terre.", "Genèse", 1, 1),
        ("Je suis la résurrection et la vie.", "Jean", 11, 25),
        ("L'Éternel est mon berger, je ne manquerai de rien.", "Psaumes", 23, 1),
    ]
    
    for verse_text, book, chap, vnum in test_cases:
        explanation = generate_smart_fallback_explanation(verse_text, book, chap, vnum)
        print(f"\n{book} {chap}:{vnum}")
        print(f"Verset: {verse_text}")
        print(f"Explication (fallback): {explanation[:200]}...")

async def test_enrichment_system():
    """Test du système d'enrichissement complet"""
    print("\n=== TEST SYSTÈME D'ENRICHISSEMENT COMPLET ===")
    
    verse_text = "Car Dieu a tant aimé le monde qu'il a donné son Fils unique..."
    book, chap, vnum = "Jean", 3, 16
    
    print(f"Test enrichissement pour {book} {chap}:{vnum}")
    print(f"Verset: {verse_text}")
    
    # Test avec enrichissement activé
    enriched_explanation = await generate_enriched_theological_explanation(
        verse_text, book, chap, vnum, enriched=True
    )
    
    print(f"\nExplication enrichie:")
    print(enriched_explanation)

def main():
    """Fonction principale de test"""
    print("🚀 Test du système d'enrichissement automatique")
    print("=" * 60)
    
    # Tests synchrones
    test_local_library()
    test_smart_fallback()
    
    # Test asynchrone
    print("\n🔄 Lancement du test d'enrichissement...")
    try:
        asyncio.run(test_enrichment_system())
    except Exception as e:
        print(f"Erreur dans le test d'enrichissement: {e}")
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    main()