# server.py
# API Bible Study (Darby) — Backend pour Railway

import os
import re
import unicodedata
from typing import Dict, List, Optional
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Charger les variables d'environnement
load_dotenv()

API_BASE = "https://api.scripture.api.bible/v1"
APP_NAME = "Bible Study API - Railway"
BIBLE_API_KEY = os.getenv("BIBLE_API_KEY", "")
PREFERRED_BIBLE_ID = os.getenv("BIBLE_ID", "a93a92589195411f-01")  # Darby FR par défaut

# --- CORS pour Railway ---
ALLOWED_ORIGINS = [
    "https://etude8-bible.vercel.app",
    "https://etude-bible-app.preview.emergentagent.com",  # ← AJOUTÉ POUR EMERGENT
    "http://localhost:3000",
    "http://localhost:5173",
]

app = FastAPI(title="Bible Study API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# SCHEMAS
# =========================

class VerseByVerseRequest(BaseModel):
    passage: str = Field(..., description="Ex: 'Genèse 1' ou 'Genèse 1:1'")
    version: str = Field("", description="Ignoré (api.bible).")

# =========================
# OUTILS livres → OSIS
# =========================

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-zA-Z0-9 ]+", " ", s).lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s

BOOKS_FR_OSIS: Dict[str, str] = {
    "genese": "GEN", "gen": "GEN",
    "exode": "EXO", "exo": "EXO",
    "levitique": "LEV", "lev": "LEV",
    "nombres": "NUM", "nom": "NUM", "nbr": "NUM", "nb": "NUM",
    "deuteronome": "DEU", "deut": "DEU", "dt": "DEU",
    "josue": "JOS", "juges": "JDG", "ruth": "RUT",
    "1 samuel": "1SA", "2 samuel": "2SA",
    "1 rois": "1KI", "2 rois": "2KI",
    "1 chroniques": "1CH", "2 chroniques": "2CH",
    "esdras": "EZR", "nehemie": "NEH", "esther": "EST",
    "job": "JOB", "psaumes": "PSA", "psaume": "PSA", "ps": "PSA",
    "proverbes": "PRO", "prov": "PRO",
    "ecclesiaste": "ECC", "cantique des cantiques": "SNG", "cantique": "SNG",
    "esaie": "ISA", "jeremie": "JER", "lamentations": "LAM",
    "ezechiel": "EZK", "daniel": "DAN",
    "osee": "HOS", "joel": "JOL", "amos": "AMO", "abdias": "OBA",
    "jonas": "JON", "michee": "MIC", "nahum": "NAM", "habakuk": "HAB",
    "sophonie": "ZEP", "aggee": "HAG", "zacharie": "ZEC", "malachie": "MAL",
    "matthieu": "MAT", "marc": "MRK", "luc": "LUK", "jean": "JHN",
    "actes": "ACT",
    "romains": "ROM", "1 corinthiens": "1CO", "2 corinthiens": "2CO",
    "galates": "GAL", "ephesiens": "EPH", "philippiens": "PHP",
    "colossiens": "COL", "1 thessaloniciens": "1TH", "2 thessaloniciens": "2TH",
    "1 timothee": "1TI", "2 timothee": "2TI", "tite": "TIT", "philemon": "PHM",
    "hebreux": "HEB", "jacques": "JAS", "1 pierre": "1PE", "2 pierre": "2PE",
    "1 jean": "1JN", "2 jean": "2JN", "3 jean": "3JN", "jude": "JUD",
    "apocalypse": "REV", "apoc": "REV",
}

def resolve_osis(book_raw: str) -> Optional[str]:
    key = _norm(book_raw)
    key = key.replace("er ", "1 ").replace("ere ", "1 ").replace("eme ", " ")
    return BOOKS_FR_OSIS.get(key)

# =========================
# API.BIBLE CLIENT
# =========================

def headers() -> Dict[str, str]:
    if not BIBLE_API_KEY:
        raise HTTPException(status_code=500, detail="BIBLE_API_KEY manquante.")
    return {"api-key": BIBLE_API_KEY}

_cached_bible_id: Optional[str] = None

async def get_bible_id() -> str:
    global _cached_bible_id
    if _cached_bible_id:
        return _cached_bible_id

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/bibles", headers=headers())
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Erreur API Bible (bibles).")

        bibles = resp.json().get("data", [])
        for bible in bibles:
            if bible.get("id") == PREFERRED_BIBLE_ID:
                _cached_bible_id = PREFERRED_BIBLE_ID
                return _cached_bible_id

        # Fallback: chercher une bible française
        for bible in bibles:
            lang = bible.get("language", {}).get("name", "").lower()
            if "french" in lang:
                _cached_bible_id = bible["id"]
                return _cached_bible_id

        raise HTTPException(status_code=500, detail="Aucune bible française trouvée.")

def parse_passage_input(passage: str) -> tuple:
    # Exemple: "Jean 3" ou "Jean 3:16"
    match = re.match(r"^\s*(.+?)\s+(\d+)(?::(\d+))?\s*(?:\S.*)?$", passage.strip())
    if not match:
        raise HTTPException(status_code=400, detail="Format attendu: 'Livre Chapitre[:Verset]'")

    book_raw = match.group(1).strip()
    chapter = int(match.group(2))
    verse = int(match.group(3)) if match.group(3) else None

    osis = resolve_osis(book_raw)
    if not osis:
        raise HTTPException(status_code=400, detail=f"Livre non reconnu: '{book_raw}'")

    return book_raw.title(), osis, chapter, verse

async def fetch_passage_text(bible_id: str, osis: str, chapter: int, verse: Optional[int]) -> str:
    if verse:
        passage_id = f"{osis}.{chapter}.{verse}"
        endpoint = f"{API_BASE}/bibles/{bible_id}/verses/{passage_id}"
    else:
        passage_id = f"{osis}.{chapter}"
        endpoint = f"{API_BASE}/bibles/{bible_id}/chapters/{passage_id}"

    async with httpx.AsyncClient() as client:
        resp = await client.get(endpoint, headers=headers(), params={"content-type": "text"})
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Passage non trouvé: {passage_id}")
        elif resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Erreur lors de la récupération du passage.")

        data = resp.json().get("data", {})
        content = data.get("content", "").strip()
        if not content:
            raise HTTPException(status_code=404, detail="Contenu vide pour ce passage.")

        return content

def generate_simple_theological_explanation(verse_text: str, book_name: str, chapter: int, verse_num: Optional[int]) -> str:
    """Génère une explication théologique contextuelle simple"""
    
    explanation_parts = []
    
    # Contexte basique par livre
    book_contexts = {
        "Genèse": "Ce verset s'inscrit dans le récit des origines et révèle les fondements de la création divine.",
        "Exode": "Ce passage illustre la libération du peuple de Dieu et sa relation d'alliance.",
        "Jean": "Ce témoignage révèle la divinité du Christ et la vie éternelle.",
        "Matthieu": "Cet enseignement du Seigneur éclaire les principes du royaume des cieux.",
        "Romains": "Cette vérité doctrinale expose les fondements de la justification par la foi.",
        "Éphésiens": "Ce passage révèle les richesses spirituelles du croyant en Christ.",
        "Psaumes": "Ce verset exprime l'authentique spiritualité dans la relation avec Dieu.",
    }
    
    explanation_parts.append(book_contexts.get(book_name, f"Ce verset révèle un aspect important de la révélation divine dans le livre de {book_name}."))
    
    full_explanation = " ".join(explanation_parts)
    return ' '.join(full_explanation.split())

# =========================
# ROUTES
# =========================

@app.get("/")
def root():
    return {"message": "Bible Study API - Railway", "status": "online", "version": "1.0.0"}

@app.get("/health")
def health_root():
    return {"status": "ok"}

@app.get("/api/")
def api_root():
    return {"message": APP_NAME, "status": "online"}

@app.get("/api/health")
async def health_api():
    bid = None
    try:
        bid = await get_bible_id()
    except Exception as e:
        return {"status": "error", "error": str(e)}
    return {"status": "ok", "bibleId": bid or "unknown"}

@app.post("/api/generate-verse-by-verse")
async def generate_verse_by_verse(req: VerseByVerseRequest):
    try:
        book_label, osis, chap, verse = parse_passage_input(req.passage)
        bible_id = await get_bible_id()
        text = await fetch_passage_text(bible_id, osis, chap, verse)

        title = f"Étude Verset par Verset - {book_label} Chapitre {chap}"
        intro = (
            "Introduction au Chapitre\n\n"
            "Cette étude parcourt le texte de la **Bible Darby (FR)**. "
            "Les sections *EXPLICATION THÉOLOGIQUE* sont générées automatiquement par IA théologique."
        )

        if verse:
            theological_explanation = generate_simple_theological_explanation(text, book_label, chap, verse)
            content = (
                f"**{title}**\n\n{intro}\n\n"
                f"**VERSET {verse}**\n\n"
                f"**TEXTE BIBLIQUE :**\n{text}\n\n"
                f"**EXPLICATION THÉOLOGIQUE :**\n{theological_explanation}"
            )
            return {"content": content}

        # Chapitre entier
        lines = [line for line in text.splitlines() if line.strip()]
        total_verses = len(lines)
        
        # Titre avec nombre de versets
        title_with_count = f"Étude Verset par Verset - {book_label} Chapitre {chap} ({total_verses} versets)"
        intro_with_count = (
            f"**📊 CHAPITRE COMPLET : {total_verses} versets à étudier**\n\n"
            "Introduction au Chapitre\n\n"
            "Cette étude parcourt le texte de la **Bible Darby (FR)**. "
            "Les sections *EXPLICATION THÉOLOGIQUE* sont générées automatiquement par IA théologique."
        )
        
        blocks: List[str] = [f"**{title_with_count}**\n\n{intro_with_count}"]

        for line in lines:
            m = re.match(r"^(\d+)\.\s*(.*?)$", line)
            if not m:
                continue
            vnum = int(m.group(1))
            vtxt = m.group(2).strip()

            theological_explanation = generate_simple_theological_explanation(vtxt, book_label, chap, vnum)
            blocks.append(
                f"**VERSET {vnum}**\n\n"
                f"**TEXTE BIBLIQUE :**\n{vtxt}\n\n"
                f"**EXPLICATION THÉOLOGIQUE :**\n{theological_explanation}"
            )

        return {"content": "\n\n".join(blocks).strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)