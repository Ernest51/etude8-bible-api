# -*- coding: utf-8 -*-
"""
Générateur 'verset par verset' enrichi
- expose VERSE_BY_VERSE_LIBRARY (ta base)
- helpers: get_verse_by_verse_content, get_all_verses_for_chapter
- enrichissement: _enrich_explanation + build_verse_by_verse_study
- parsing simple: parse_passage
"""

from typing import Dict, List, Tuple, Optional
import re

# =====================================================================
# 1) TA BASE DE DONNÉES — mets ICI ton dictionnaire complet (sans tronquer)
# =====================================================================

VERSE_BY_VERSE_LIBRARY: Dict[str, Dict[int, Dict[int, Dict[str, str]]]] = {
    # ⬇️ EXEMPLES (pour validation). Remplace/complète par ton dump intégral.
    "Genèse": {
        1: {
            1: {
                "verse": "Au commencement, Dieu créa les cieux et la terre.",
                "explanation": (
                    "Au commencement (Bereshit) affirme l’origine absolue du temps et de la matière. "
                    "Dieu (Elohim), pluriel de majesté, laisse entrevoir la Trinité. "
                    "Créa (bara) : création ex nihilo, acte souverain. "
                    "Les cieux et la terre : totalité du cosmos visible et invisible."
                ),
            },
            2: {
                "verse": "La terre était informe et vide...",
                "explanation": (
                    "Tohu va-bohu indique l’absence d’ordre et de contenu. "
                    "L’Esprit de Dieu (ruach Elohim) plane : préparation de l’ordre par la présence divine."
                ),
            },
        }
    },
    "Exode": {
        1: {
            1: {
                "verse": "Voici les noms des fils d’Israël, venus en Égypte...",
                "explanation": (
                    "La liste ouvre l’Exode sur la mémoire des promesses : Dieu connaît ses élus par leur nom. "
                    "Transition de Genèse à Exode sous le signe de la fidélité."
                ),
            },
            2: {
                "verse": "Ruben, Siméon, Lévi et Juda;",
                "explanation": (
                    "Énumération tribale : chaque nom porte une trajectoire prophétique (cf. Gn 49). "
                    "Juda, tribu messianique, prépare la lignée royale."
                ),
            },
        },
        2: {
            1: {
                "verse": "Un homme de la maison de Lévi avait pris pour femme une fille de Lévi.",
                "explanation": (
                    "Providence : Moïse naît dans la lignée sacerdotale. "
                    "Dieu façonne son instrument dans l’adversité."
                ),
            }
        },
    },
    "Jean": {
        1: {
            1: {
                "verse": "Au commencement était la Parole...",
                "explanation": (
                    "Le Logos préexistant est auprès de Dieu et est Dieu. "
                    "Fondement trinitaire et christologie haute du prologue."
                ),
            },
            3: {
                "verse": "Toutes choses ont été faites par elle...",
                "explanation": (
                    "Médiation créatrice du Fils : rien de créé n’existe en dehors de Lui. "
                    "Le Christ créateur est aussi le rédempteur."
                ),
            },
        },
        3: {
            16: {
                "verse": "Car Dieu a tant aimé le monde...",
                "explanation": (
                    "Motif du salut : l’amour de Dieu ; moyen : le don du Fils unique ; "
                    "but : la vie éternelle par la foi vivante."
                ),
            }
        },
    },
}
# =====================================================================


# =====================================================================
# 2) ACCÈS "BASIC"
# =====================================================================

def get_verse_by_verse_content(book: str, chapter: int) -> dict:
    """Retourne le mapping {verse_number: {verse, explanation}} pour un chapitre."""
    return VERSE_BY_VERSE_LIBRARY.get(book, {}).get(chapter, {})

def get_all_verses_for_chapter(book: str, chapter: int) -> List[dict]:
    """Retourne la liste ordonnée des versets d’un chapitre avec texte + explication."""
    chapter_content = get_verse_by_verse_content(book, chapter)
    verses = []
    for verse_num in sorted(chapter_content.keys()):
        verse_data = chapter_content[verse_num]
        verses.append({
            "verse_number": verse_num,
            "verse_text": verse_data.get("verse", ""),
            "explanation": verse_data.get("explanation", "")
        })
    return verses


# =====================================================================
# 3) ENRICHISSEMENT (sans LLM)
# =====================================================================

def _md_inline(s: str) -> str:
    """Nettoyage léger pour éviter toute injection Markdown."""
    s = s or ""
    return s.replace("```", "ʼʼʼ")

def _limit_by_tokens(text: str, tokens: int) -> str:
    """
    Découpage approximatif par tokens (~5 chars/token).
    Conserve la lisibilité (coupe à la fin d’un paragraphe/phrase si possible).
    """
    if not tokens or tokens <= 0:
        return text
    approx_chars = max(200, tokens * 5)
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

def _enrich_explanation(
    book: str,
    chapter: int,
    verse_num: int,
    verse_text: str,
    explanation: str,
    detail_level: str = "basic"
) -> str:
    """
    Produit une explication structurée, sans LLM, à partir du commentaire existant.
    detail_level:
      - basic  : commentaire tel quel
      - rich   : + Contexte / Lexique / Parallèles / Doctrine / Application
      - expert : rich + Prière
    """
    explanation = explanation or ""
    verse_text = verse_text or ""

    if detail_level == "basic":
        return _md_inline(explanation).strip()

    # Contexte (heuristique)
    if re.search(r"(histoire|contexte|culture|égypte|désert|patriar|roya|exil|temple|pâque|sabbat)", explanation, re.I):
        context_line = "- **Contexte** : éléments historiques/culturels explicités."
    else:
        context_line = "- **Contexte** : situe le verset dans le récit et son cadre historique."

    # Lexique (heuristique)
    if re.search(r"(hébreu|grec|pluriel|bara|ruach|logos|agap|qadash|berit)", explanation, re.I):
        lex_line = "- **Analyse lexicale** : termes clés déjà évoqués (hébreu/grec) et leur portée."
    else:
        lex_line = "- **Analyse lexicale** : 1–2 termes significatifs (racine, sens, théologie)."

    # Parallèles
    par_line = "- **Parallèles bibliques** : "
    if book.lower().startswith("gen"):
        par_line += "Jean 1; Hébreux 11; Psaume 33."
    elif book.lower().startswith("exo"):
        par_line += "Hébreux 3–4; 1 Corinthiens 10; Deutéronome 6."
    elif book.lower().startswith("jean"):
        par_line += "Genèse 1; Colossiens 1; Hébreux 1."
    else:
        par_line += "renvois canoniques pertinents."

    doc_line = "- **Doctrine / Christ au centre** : relier le verset à l’économie du salut et à la personne du Christ."
    app_line = "- **Application** : implications personnelles (foi/vertus) et communautaires (Église/mission)."

    blocks = [
        _md_inline(explanation).strip(),
        "",
        "—",
        context_line,
        lex_line,
        par_line,
        doc_line,
        app_line,
    ]

    if detail_level == "expert":
        blocks.append("- **Prière** : 2–3 phrases (adoration, confession, supplication).")

    return "\n".join(blocks).strip()

def build_verse_by_verse_study(
    book: str,
    chapter: int,
    *,
    version: str = "LSG",
    detail_level: str = "basic",
    tokens: int = 500,
    start_verse: int = 1,
    batch_size: Optional[int] = None,
    only_verse: Optional[int] = None,
) -> Tuple[str, int, int]:
    """
    Construit un rendu 'Étude verset par verset'.
    Retourne (content, last_verse_included, total_verses_in_chapter)
    - only_verse : génère uniquement ce verset
    - batch_size : génère un bloc à partir de start_verse
    """
    chapter_map = VERSE_BY_VERSE_LIBRARY.get(book, {}).get(chapter, {})
    # si base absente, squelette générique
    if not chapter_map:
        total = 30
        v_start = only_verse or start_verse or 1
        v_end = v_start if only_verse else min(total, v_start + (batch_size or total) - 1)

        parts = [f"### {book} {chapter} ({version}) — Étude verset par verset\n"]
        for v in range(v_start, v_end + 1):
            parts += [
                f"\nVERSET {v}\n",
                "TEXTE BIBLIQUE :\n",
                f"[{v}] (texte non renseigné dans la base)",
                "\nEXPLICATION THÉOLOGIQUE :\n",
                _enrich_explanation(book, chapter, v, "", "Commentaire non disponible.", detail_level),
                "\n"
            ]
        content = _limit_by_tokens("\n".join(parts), tokens)
        return content, v_end, total

    verse_numbers = sorted(chapter_map.keys())
    total_verses = len(verse_numbers)

    # plage de versets
    if only_verse:
        rng = [only_verse]
    else:
        v_start = max(1, start_verse or 1)
        v_end = verse_numbers[-1] if not batch_size else min(verse_numbers[-1], v_start + batch_size - 1)
        rng = list(range(v_start, v_end + 1))

    parts = [f"### {book} {chapter} ({version}) — Étude verset par verset\n"]
    for v in rng:
        data = chapter_map.get(v, {})
        verse_text = data.get("verse", "")
        explanation = data.get("explanation", "")
        parts += [
            f"\nVERSET {v}\n",
            "TEXTE BIBLIQUE :\n",
            f"[{v}] {verse_text}",
            "\nEXPLICATION THÉOLOGIQUE :\n",
            _enrich_explanation(book, chapter, v, verse_text, explanation, detail_level),
            "\n"
        ]

    content = _limit_by_tokens("\n".join(parts), tokens)
    last_included = rng[-1] if rng else 0
    return content, last_included, total_verses


# =====================================================================
# 4) PARSING
# =====================================================================

BOOK_NAMES = list(VERSE_BY_VERSE_LIBRARY.keys())

def _resolve_book_name(raw: str) -> str:
    raw_l = raw.lower()
    for b in BOOK_NAMES:
        bl = b.lower()
        if bl == raw_l or bl.startswith(raw_l) or raw_l.startswith(bl):
            return b
    return raw

def parse_passage(p: str) -> Tuple[str, int, Optional[int]]:
    """
    Parse 'Exode 1', 'Genèse 1:3' → (book, chapter, verse|None)
    """
    s = (p or "").strip()
    if not s:
        return ("", 0, None)

    m = re.match(r"^(.+?)\s+(\d+):(\d+)$", s)
    if m:
        book_raw = m.group(1).strip()
        chapter = int(m.group(2))
        verse = int(m.group(3))
        book = _resolve_book_name(book_raw)
        return (book, chapter, verse)

    m = re.match(r"^(.+?)\s+(\d+)$", s)
    if m:
        book_raw = m.group(1).strip()
        chapter = int(m.group(2))
        book = _resolve_book_name(book_raw)
        return (book, chapter, None)

    # 'Livre' simple → chapitre 1 par défaut
    book = _resolve_book_name(s)
    return (book, 1, None)
