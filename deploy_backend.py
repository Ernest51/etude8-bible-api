#!/usr/bin/env python3
"""
Script pour tester si notre backend enrichi fonctionne avec Railway
"""

import os
import sys
sys.path.append('/app/backend')

# Test direct du backend enrichi
from server import generate_enriched_theological_explanation
import asyncio

async def test_enrichment():
    print("🔍 Test de l'enrichissement direct...")
    
    verse_text = "Au commencement, Dieu créa les cieux et la terre."
    result = await generate_enriched_theological_explanation(verse_text, "Genèse", 1, 1, enriched=True)
    
    print(f"📊 Longueur: {len(result)} caractères")
    print(f"📝 Aperçu: {result[:200]}...")
    
    if len(result) > 500 and "ANALYSE TEXTUELLE" in result:
        print("✅ ENRICHISSEMENT FONCTIONNE!")
        return True
    else:
        print("❌ Enrichissement défaillant")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enrichment())
    sys.exit(0 if success else 1)