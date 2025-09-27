# -*- coding: utf-8 -*-
"""
Générateur d'étude théologique "chapitre" (style riche)
- conserve THEOLOGICAL_LIBRARY existant
- produit une étude structurée (rubriques fortes)
- supporte detail_level + tokens
"""

from typing import Dict
import re

THEOLOGICAL_LIBRARY: Dict[str, Dict[int, dict]] = {
    # ---------- colle ici ton dictionnaire tel quel ----------
    # ... tes données inchangées (Genèse, Exode, Jean, etc.) ...
}

def get_theological_content(book: str, chapter: int) -> dict:
    """Retour brut depuis la lib (inchangé)"""
    return THEOLOGICAL_LIBRARY.get(book, {}).get(chapter, {
        "title": f"Étude Théologique de {book} {chapter}",
        "narrative": f"Cette étude approfondie de **{book} chapitre {chapter}** révèle les richesses doctrinales de la Parole de Dieu.",
        "theological_points": [
            f"**Contexte canonique** : {book} {chapter} dans l'économie divine",
            f"**Enseignement doctrinal** : Vérités révélées dans ce passage",
            f"**Application pratique** : Transformation spirituelle attendue",
            f"**Perspective christologique** : Christ révélé ou préfiguré"
        ]
    })

def _limit_by_tokens(text: str, tokens: int) -> str:
    if not tokens or tokens <= 0:
        return text
    approx_chars = max(300, tokens * 5)
    if len(text) <= approx_chars:
        return text
    cut = text[:approx_chars]
    last_para = cut.rfind("\n\n")
    if last_para > 400:
        cut = cut[:last_para].rstrip()
    else:
        last_sentence = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
        if last_sentence > 400:
            cut = cut[:last_sentence + 1]
    return cut + "\n\n*…(suite abrégée)*"

def build_theological_study(
    book: str,
    chapter: int,
    *,
    version: str = "LSG",
    detail_level: str = "rich",
    tokens: int = 1000
) -> str:
    """
    Construit une étude '28 points' style riche (markdown-like simple)
    """
    base = get_theological_content(book, chapter)
    title = base.get("title") or f"Étude Théologique de {book} {chapter}"
    narrative = base.get("narrative", "")
    points = base.get("theological_points", [])

    blocs = [
        f"## {title}\n",
        f"**Passage** : {book} {chapter} ({version})\n",
        narrative.strip(),
        "",
        "### Contexte historique & culturel",
        "- Cadre temporel, acteurs principaux, géographie, enjeux de l’alliance.",
        "",
        "### Structure littéraire",
        "- Découpage du passage, motifs, progression argumentative/rhéthorique.",
        "",
        "### Th
