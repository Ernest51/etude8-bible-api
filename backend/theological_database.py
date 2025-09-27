# -*- coding: utf-8 -*-
"""
Générateur d'étude théologique 'chapitre'
- THEOLOGICAL_LIBRARY : ta base chapitrée
- get_theological_content(book, chapter)
- build_theological_study(book, chapter, detail_level, tokens)
- utilitaires : get_historical_context / get_cross_references
- façade 'theological_db' (compat serveur)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

# =====================================================================
# 1) TA BASE CHAPITRÉE — mets ICI ton dictionnaire complet (sans tronquer)
# =====================================================================

THEOLOGICAL_LIBRARY: Dict[str, Dict[int, dict]] = {
    # ⬇️ EXEMPLES minimaux. Remplace/complète par ton dump intégral.
    "Genèse": {
        4: {
            "title": "Caïn et Abel : grâce et jugement aux origines",
            "narrative": (
                "La tension post-chute culmine dans l’opposition foi/œuvre. "
                "L’offrande d’Abel par la foi préfigure l’Agneau parfait ; la colère de Caïn révèle l’orgueil religieux."
            ),
            "theological_points": [
                "Spiritualité authentique vs ritualisme.",
                "Typologie sacrificielle et annonce du Christ.",
                "Éthique fraternelle et responsabilité morale."
            ],
        },
    },
    "Exode": {
        2: {
            "title": "Formation de Moïse : providence en temps d’adversité",
            "narrative": (
                "Moïse, tiré des eaux, est préparé dans la maison de Pharaon. "
                "Dieu forme ses instruments avant l’envoi."
            ),
            "theological_points": [
                "Souveraineté de Dieu dans l’histoire.",
                "Vocation et préparation de l’envoyé.",
                "Rédemption annoncée par figure."
            ],
        },
    },
    "Jean": {
        1: {
            "title": "Le Logos éternel : révélation suprême",
            "narrative": (
                "Le prologue dévoile la divinité du Christ, Parole créatrice et révélatrice, "
                "source de vie et de lumière."
            ),
            "theological_points": [
                "Christologie haute (préexistence, divinité).",
                "Création par le Fils.",
                "Révélation et salut."
            ],
        },
    },
}
# =====================================================================


# =====================================================================
# 2) APIS
# =====================================================================

def get_theological_content(book: str, chapter: int) -> dict:
    """Retourne le bloc chapitré si présent, sinon un gabarit riche générique."""
    return THEOLOGICAL_LIBRARY.get(book, {}).get(chapter, {
        "title": f"Étude Théologique de {book} {chapter}",
        "narrative": (
            f"Étude de **{book} {chapter}** : mise en contexte canonique, doctrine, "
            "application et christologie."
        ),
        "theological_points": [
            f"Contexte canonique de {book} {chapter}",
            "Enseignement doctrinal principal",
            "Applications pratiques (vie personnelle et communautaire)",
            "Perspective christocentrique",
        ],
    })


# =====================================================================
# 3) UTILITAIRES (facultatifs mais utiles)
# =====================================================================

@dataclass
class CrossReference:
    book: str
    chapter: int
    verse: Optional[int] = None
    context: str = ""

def get_historical_context(book: str, chapter: int) -> str:
    """Contexte historique générique (remplaçable par du précis)."""
    templates = {
        "Genèse": "Période des origines et des patriarches ; mise en place des alliances.",
        "Exode": "Oppression en Égypte, délivrance, alliance sinaïtique.",
        "Jean": "Judée du Second Temple ; ministère de Jésus sous occupation romaine.",
    }
    return templates.get(book, "Contexte historique à préciser selon le livre.")

def get_cross_references(book: str, chapter: int) -> List[CrossReference]:
    """Renvois canoniques génériques (remplaçables par tes propres tables)."""
    if book == "Genèse" and chapter == 1:
        return [
            CrossReference("Psaumes", 33, 6, "Par la parole de l’Éternel les cieux furent faits."),
            CrossReference("Jean", 1, 1, "Le Logos créateur."),
            CrossReference("Hébreux", 11, 3, "Le monde a été formé par la parole de Dieu."),
        ]
    if book == "Jean" and chapter == 1:
        return [
            CrossReference("Genèse", 1, 1, "Écho du commencement."),
            CrossReference("Colossiens", 1, 16, "Tout a été créé par lui et pour lui."),
        ]
    return []


# =====================================================================
# 4) CONSTRUCTEUR '28 RUBRIQUES' (style riche, markdown-like)
# =====================================================================

def build_theological_study(
    book: str,
    chapter: int,
    *,
    version: str = "LSG",
    detail_level: str = "rich",
    tokens: int = 1000
) -> str:
    """
    Construit une étude en rubriques solides (utilisable même sans LLM).
    """
    base = get_theological_content(book, chapter)
    title = base.get("title") or f"Étude Théologique de {book} {chapter}"
    narrative = base.get("narrative", "")
    points = base.get("theological_points", [])

    hist = get_historical_context(book, chapter)
    refs = get_cross_references(book, chapter)
    refs_txt = ""
    if refs:
        refs_txt = "\n".join(
            [f"- {r.book} {r.chapter}{(':'+str(r.verse)) if r.verse else ''} — {r.context}".rstrip()
             for r in refs]
        )

    blocs = [
        f"# {title}",
        f"**Passage** : {book} {chapter} ({version})",
        "",
        "## 1. Prière d'ouverture",
        "Père, ouvre nos cœurs et nos intelligences à ta Parole ; conduis-nous dans la vérité.",
        "",
        "## 2. Structure littéraire",
        "Découpage du passage, progression rhétorique et motifs principaux.",
        "",
        "## 3. Questions du chapitre précédent",
        "Quels enjeux précédents trouvent ici une réponse ou un développement ?",
        "",
        "## 4. Thème doctrinal",
        (points[0] if points else "Doctrine principale mise en lumière par le passage."),
        "",
        "## 5. Fondements théologiques",
        "Lien avec l’alliance, la loi, la promesse, la sagesse, la prophétie.",
        "",
        "## 6. Contexte historique",
        hist,
        "",
        "## 7. Contexte culturel",
        "Usages et référents culturels utiles à l’interprétation.",
        "",
        "## 8. Contexte géographique",
        "Lieux, itinéraires, portée symbolique des espaces.",
        "",
        "## 9. Analyse lexicale",
        "Termes clefs (hébreu/grec), champs sémantiques et portée théologique.",
        "",
        "## 10. Parallèles bibliques",
        refs_txt or "Autres passages éclairant ce texte dans l’unité du canon.",
        "",
        "## 11. Prophétie et accomplissement",
        "Attentes messianiques et accomplissements en Christ.",
        "",
        "## 12. Personnages",
        "Rôles, vertus et faillibilités ; trajectoires spirituelles.",
        "",
        "## 13. Structure rhétorique",
        "Figures, symétries, inclusions, climax.",
        "",
        "## 14. Théologie trinitaire",
        "Indices de l’action du Père, du Fils et de l’Esprit.",
        "",
        "## 15. Christ au centre",
        (points[2] if len(points) >= 3 else "Christ révélé/préfiguré dans le passage."),
        "",
        "## 16. Évangile et grâce",
        "Grâce, pardon, réconciliation, vie nouvelle.",
        "",
        "## 17. Application personnelle",
        "Vertus, prières, disciplines, espérance.",
        "",
        "## 18. Application communautaire",
        "Église, unité, mission, service.",
        "",
        "## 19. Prière de réponse",
        "Seigneur, grave ces vérités en nous et conduis nos vies selon ta volonté.",
        "",
        "## 20. Questions d'étude",
        "- Qu’enseigne le texte sur Dieu ?\n- Sur l’homme ?\n- Sur le salut ?",
        "",
        "## 21. Points de vigilance",
        "Écueils d’interprétation, lectures réductrices à éviter.",
        "",
        "## 22. Objections et réponses",
        "Questions fréquentes et éléments de réponse fidèles à l’Écriture.",
        "",
        "## 23. Perspective missionnelle",
        "Implications pour le témoignage et la justice du Royaume.",
        "",
        "## 24. Éthique chrétienne",
        "Commandements, vertus, sagesse pratique.",
        "",
        "## 25. Louange / liturgie",
        "Pistes de louange, confession, intercession.",
        "",
        "## 26. Méditation guidée",
        "Silence, rumination du texte, prière.",
        "",
        "## 27. Mémoire / versets clés",
        "Sélection de versets à mémoriser.",
        "",
        "## 28. Plan d'action",
        "Étapes concrètes et mesurables à mettre en œuvre.",
        "",
        "—",
        "### Narratif synthétique",
        narrative if narrative else "Résumé théologique du chapitre.",
    ]

    # (Optionnel) limitation soft par longueur
    txt = "\n".join(blocs).strip()
    if tokens and tokens > 0:
        approx_chars = max(600, tokens * 5)
        if len(txt) > approx_chars:
            txt = txt[:approx_chars].rsplit("\n", 1)[0].rstrip() + "\n\n*…(suite abrégée)*"

    return txt


# =====================================================================
# 5) FACILITER LES IMPORTS (compatibilité serveur.py)
# =====================================================================

class _Facade:
    get_historical_context = staticmethod(get_historical_context)
    get_cross_references = staticmethod(get_cross_references)

theological_db = _Facade()
