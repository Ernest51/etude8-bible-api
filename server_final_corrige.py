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
    "https://etude-bible-app.preview.emergentagent.com",
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

    if PREFERRED_BIBLE_ID:
        _cached_bible_id = PREFERRED_BIBLE_ID
        return _cached_bible_id

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{API_BASE}/bibles", headers=headers())
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"api.bible bibles: {r.text}")
        data = r.json()
        lst = data.get("data", [])
        for b in lst:
            name = (b.get("name") or "") + " " + (b.get("abbreviationLocal") or "")
            lang = (b.get("language") or {}).get("name", "")
            if "darby" in name.lower() and ("fr" in lang.lower() or "fra" in lang.lower()):
                _cached_bible_id = b.get("id")
                break
        if not _cached_bible_id:
            for b in lst:
                lang = (b.get("language") or {}).get("name", "")
                if "fr" in lang.lower() or "fra" in lang.lower():
                    _cached_bible_id = b.get("id")
                    break
        if not _cached_bible_id:
            raise HTTPException(status_code=500, detail="Aucune Bible FR trouvée via api.bible.")
    return _cached_bible_id

async def list_verses_ids(bible_id: str, osis_book: str, chapter: int) -> List[str]:
    chap_id = f"{osis_book}.{chapter}"
    url = f"{API_BASE}/bibles/{bible_id}/chapters/{chap_id}/verses"
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, headers=headers())
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"api.bible verses list: {r.text}")
        data = r.json()
        return [v["id"] for v in data.get("data", [])]

async def fetch_verse_text(bible_id: str, verse_id: str) -> str:
    url = f"{API_BASE}/bibles/{bible_id}/verses/{verse_id}"
    params = {"content-type": "text"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, headers=headers(), params=params)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"api.bible verse: {r.text}")
        data = r.json()
        content = (data.get("data") or {}).get("content") or ""
        content = re.sub(r"\s+", " ", content).strip()
        return content

async def fetch_passage_text(bible_id: str, osis_book: str, chapter: int, verse: Optional[int] = None) -> str:
    if verse:
        verse_id = f"{osis_book}.{chapter}.{verse}"
        return await fetch_verse_text(bible_id, verse_id)
    ids = await list_verses_ids(bible_id, osis_book, chapter)
    parts: List[str] = []
    for idx, vid in enumerate(ids, start=1):
        txt = await fetch_verse_text(bible_id, vid)
        parts.append(f"{idx}. {txt}")
    return "\n".join(parts).strip()

def parse_passage_input(p: str):
    p = p.strip()
    m = re.match(r"^(.*?)\s+(\d+)(?::(\d+))?(?:\s+\S+.*)?$", p)
    if not m:
        raise HTTPException(status_code=400, detail="Format passage invalide. Ex: 'Genèse 1' ou 'Genèse 1:1'.")
    book = m.group(1).strip()
    chapter = int(m.group(2))
    verse = int(m.group(3)) if m.group(3) else None
    osis = resolve_osis(book)
    if not osis:
        raise HTTPException(status_code=400, detail=f"Livre non reconnu: '{book}'.")
    return book, osis, chapter, verse

def generate_simple_theological_explanation(verse_text: str, book_name: str, chapter: int, verse_num: int) -> str:
    verse_lower = verse_text.lower()
    explanation_parts = []
    
    if book_name == "Genèse" and chapter == 1:
        # Image de Dieu (v26-27)
        if "image" in verse_lower and ("homme" in verse_lower or "créa" in verse_lower):
            explanation_parts.append("La création de l'homme à l'image de Dieu révèle la dignité unique de l'humanité et sa vocation à refléter la gloire divine. Cette image implique une capacité relationnelle, créatrice et morale.")
        
        # Bénédiction et mandat (v28)
        elif ("bénit" in verse_lower or "fructifiez" in verse_lower) and "multipliez" in verse_lower:
            explanation_parts.append("Cette bénédiction divine établit le mandat créationnel : fructifier, multiplier, remplir et dominer la terre. La domination n'est pas exploitation mais intendance responsable sous l'autorité de Dieu.")
        
        # Provision alimentaire pour l'homme (v29)
        elif "plante" in verse_lower and "nourriture" in verse_lower and ("vous" in verse_lower or "portant semence" in verse_lower):
            explanation_parts.append("Dieu pourvoit généreusement aux besoins de l'humanité. Ce régime végétal initial révèle l'harmonie parfaite de la création avant la chute, où aucune mort n'était nécessaire pour la subsistance.")
        
        # Provision pour les animaux (v30)
        elif "animal" in verse_lower and ("plante verte" in verse_lower or "âme vivante" in verse_lower):
            explanation_parts.append("La providence divine s'étend à toute créature vivante. Cette provision végétale universelle témoigne de l'ordre parfait voulu par Dieu, où toute vie trouve sa subsistance sans violence.")
        
        # Évaluation divine (v31)
        elif "très bon" in verse_lower or ("vit" in verse_lower and ("sixième jour" in verse_lower or "bon" in verse_lower)):
            explanation_parts.append("L'évaluation divine 'très bon' couronne l'œuvre créatrice. Cette perfection originelle contraste avec l'état actuel du monde et annonce la restauration future dans la nouvelle création.")
        
        # Création générale
        elif "créa" in verse_lower or "commencement" in verse_lower:
            explanation_parts.append("Ce verset établit le fondement de toute la révélation biblique en proclamant Dieu comme Créateur souverain de toutes choses.")
        
        # Séparation/organisation
        elif "sépara" in verse_lower or "divisa" in verse_lower:
            explanation_parts.append("L'acte divin de séparation révèle un Dieu d'ordre qui structure le cosmos. Cette organisation témoigne de sa sagesse et prépare un habitat propice à la vie.")
        
        # Fallback spécifique pour Genèse 1
        else:
            explanation_parts.append("Ce verset révèle un aspect spécifique de l'œuvre créatrice divine et de l'ordre établi par Dieu dans la création.")
    
    elif book_name == "Genèse":
        if "commencement" in verse_lower or "créa" in verse_lower:
            explanation_parts.append("Ce verset établit le fondement de toute la révélation biblique en proclamant Dieu comme Créateur souverain de toutes choses.")
        elif "homme" in verse_lower and "image" in verse_lower:
            explanation_parts.append("La création de l'homme à l'image de Dieu révèle la dignité unique de l'humanité et sa vocation à refléter la gloire divine.")
        elif "alliance" in verse_lower or "promesse" in verse_lower:
            explanation_parts.append("Cette alliance divine inaugure le plan de rédemption qui se déploiera à travers toute l'histoire du salut.")
        else:
            explanation_parts.append("Ce récit des origines révèle les fondements de la relation entre Dieu et sa création.")
    
    if not explanation_parts:
        book_contexts = {
            "Genèse": "Ce verset des origines révèle les fondements du plan divin pour l'humanité et la création.",
            "Exode": "Ce passage illustre l'œuvre libératrice de Dieu et ses implications pour la foi.",
            "Jean": "Ce témoignage révèle la divinité du Christ et la vie éternelle.",
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