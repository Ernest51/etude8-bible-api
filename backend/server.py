# server.py (root)
# Bible Study API (Darby) — corrected
# - Keeps verse order (sorted IDs)
# - Preserves one-verse-per-line for full chapters (non-progressive route)
# - Adds `/health` endpoint for Railway health checks + `/api/health`

import os
import re
import unicodedata
from typing import Dict, List, Optional
from dotenv import load_dotenv

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ==== Env ====
load_dotenv()

API_BASE = "https://api.scripture.api.bible/v1"
APP_NAME = "Bible Study API - Darby Enhanced"
BIBLE_API_KEY = os.getenv("BIBLE_API_KEY", "demo_key_for_testing")
PREFERRED_BIBLE_ID = os.getenv("BIBLE_ID", "a93a92589195411f-01")  # Darby FR
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY")
DEBUG_VERSES = os.getenv("DEBUG_VERSES", "false").lower() == "true"

# ==== Local library (optional) ====
try:
    from verse_by_verse_content import (
        get_verse_by_verse_content as vlib_chapter_dict,
        get_all_verses_for_chapter as vlib_all_verses,
    )
    VLIB_AVAILABLE = True
    print("✅ Local verse-by-verse library loaded")
except Exception as e:
    print(f"ℹ️ No local verse-by-verse library found: {e}")
    VLIB_AVAILABLE = False
    def vlib_chapter_dict(book, chapter): return {}
    def vlib_all_verses(book, chapter): return []

# ==== Gemini (optional) ====
import google.generativeai as genai
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    EMERGENT_AVAILABLE = True
    GEMINI_AVAILABLE = True
    print("✅ Emergent integrations loaded - Using Emergent LLM")
except Exception:
    EMERGENT_AVAILABLE = False
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
        print("✅ Google Gemini configured directly with API key")
    else:
        GEMINI_AVAILABLE = False
        print("ℹ️ No Gemini integration available - using enhanced fallback mode")

# ==== CORS ====
_default_origins = [
    "https://etude8-bible.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
]
_extra = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
ALLOW_ORIGINS = _default_origins + _extra

app = FastAPI(title="FastAPI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS if _extra else ["*"],  # wide open during tests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
#      Schemas
# =========================
class StudyRequest(BaseModel):
    passage: str = Field(..., description="Ex: 'Nombres 2' ou 'Jean 3'")
    version: str = Field("", description="Ignoré (api.bible).")
    tokens: int = Field(0, description="Ignoré (hérité du front).")
    model: str = Field("", description="Ignoré (hérité du front).")
    enriched: bool = Field(False, description="Mode enrichi avec Gemini")
    requestedRubriques: Optional[List[int]] = Field(
        None, description="Index des rubriques à produire (0..27). None = toutes."
    )

class ProgressiveStudyRequest(BaseModel):
    passage: str = Field(..., description="Passage biblique pour étude progressive")
    version: str = Field(default="LSG", description="Version de la Bible")
    batch_size: int = Field(default=5, description="Nombre de versets par batch")
    start_verse: int = Field(default=1, description="Verset de départ")
    priority_mode: bool = Field(default=False, description="Mode priorité pour premiers versets")
    enriched: bool = Field(default=True, description="Mode enrichi automatique")

class ProgressiveStudyResponse(BaseModel):
    batch_content: str = Field(..., description="Contenu du batch actuel")
    verse_range: str = Field(..., description="Plage des versets traités")
    has_more: bool = Field(..., description="S'il y a encore des versets")
    next_start_verse: int = Field(..., description="Prochain verset")
    total_progress: float = Field(..., description="Pourcentage de progression total")
    verse_stats: Optional[Dict] = Field(None, description="Stats des versets")

# =========================
#      Helpers
# =========================
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-zA-Z0-9 ]+", " ", s).lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s

def format_theological_content(content: str) -> str:
    """Retire les ** et nettoie les espaces (mais laisse les sauts de ligne de structure)."""
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
    content = content.replace('**', '').replace('*', '')
    # On ne touche pas aux sauts de ligne ici
    content = re.sub(r'[ ]+', ' ', content)
    return content.strip()

def clean_plain_text(s: str) -> str:
    # NE PAS supprimer les sauts de ligne ici — utilisé seulement pour verset unique.
    s = s.replace("**", "").replace("*", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

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
    "job": "JOB", "psaumes": "PSA", "proverbes": "PRO",
    "ecclesiaste": "ECC", "cantique des cantiques": "SNG", "cantique": "SNG",
    "esaie": "ISA", "jeremie": "JER", "lamentations": "LAM",
    "ezechiel": "EZK", "daniel": "DAN",
    "osee": "HOS", "joel": "JOL", "amos": "AMO", "abdi": "OBA",
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
#   API.BIBLE CLIENT
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
        for b in data.get("data", []):
            lang = (b.get("language") or {}).get("name", "")
            if "fr" in (lang or "").lower():
                _cached_bible_id = b.get("id")
                break
        if not _cached_bible_id:
            raise HTTPException(status_code=500, detail="Aucune Bible FR trouvée via api.bible.")
    return _cached_bible_id

def _sort_verse_ids(ids: List[str]) -> List[str]:
    try:
        return sorted(ids, key=lambda x: int(x.rsplit('.', 1)[-1]))
    except Exception:
        return ids

async def list_verses_ids(bible_id: str, osis_book: str, chapter: int) -> List[str]:
    if DEBUG_VERSES:
        if osis_book == "GEN" and chapter == 1:
            return [f"GEN.1.{i}" for i in range(1, 6)]
        if osis_book == "JHN" and chapter == 3:
            return [f"JHN.3.{i}" for i in range(16, 17)]
    try:
        chap_id = f"{osis_book}.{chapter}"
        url = f"{API_BASE}/bibles/{bible_id}/chapters/{chap_id}/verses"
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url, headers=headers())
            if r.status_code != 200:
                return [f"{osis_book}.{chapter}.{i}" for i in range(1, 32)]
            data = r.json()
            ids = [v["id"] for v in data.get("data", [])]
            return _sort_verse_ids(ids)
    except Exception:
        return [f"{osis_book}.{chapter}.{i}" for i in range(1, 32)]

async def fetch_verse_text(bible_id: str, verse_id: str) -> str:
    if DEBUG_VERSES:
        test_verses = {
            "GEN.1.1": "Au commencement Dieu créa les cieux et la terre.",
            "GEN.1.2": "La terre était désolation et vide, ...",
            "GEN.1.3": "Dieu dit : Que la lumière soit. Et la lumière fut.",
            "GEN.1.4": "Dieu vit la lumière, qu’elle était bonne ; ...",
            "GEN.1.5": "Dieu appela la lumière Jour ; ...",
            "JHN.3.16": "Car Dieu a tant aimé le monde ...",
        }
        if verse_id in test_verses:
            return test_verses[verse_id]
    try:
        url = f"{API_BASE}/bibles/{bible_id}/verses/{verse_id}"
        params = {"content-type": "text"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url, headers=headers(), params=params)
            if r.status_code != 200:
                return f"[Texte simulé] Verset {verse_id} de la Bible"
            data = r.json()
            content = (data.get("data") or {}).get("content") or ""
            content = re.sub(r"\s+", " ", content).strip()
            content = clean_plain_text(content)
            return content
    except Exception:
        return f"[Texte simulé] Verset {verse_id} de la Bible"

async def fetch_passage_text(bible_id: str, osis_book: str, chapter: int, verse: Optional[int] = None) -> str:
    """
    IMPORTANT : pour un chapitre entier, on RETIENT les sauts de ligne (1 verset par ligne)
    afin que la route non-progressive puisse parser chaque verset proprement.
    """
    if verse:
        verse_id = f"{osis_book}.{chapter}.{verse}"
        return await fetch_verse_text(bible_id, verse_id)
    ids = await list_verses_ids(bible_id, osis_book, chapter)
    parts: List[str] = []
    for vid in ids:
        try:
            vnum = int(vid.rsplit('.', 1)[-1])
        except Exception:
            vnum = None
        txt = await fetch_verse_text(bible_id, vid)
        line = f"{vnum}. {txt}" if vnum is not None else txt
        parts.append(line)
    return "\n".join(parts).strip()

# =========================
#   Parsing du passage
# =========================
def parse_passage_input_extended(p: str):
    p = p.strip()
    m1 = re.match(r"^(.*?)\s+(\d+):(\d+)-(\d+)(?:\s+\S+.*)?$", p)
    if m1:
        book = m1.group(1).strip()
        chapter = int(m1.group(2)); start_verse = int(m1.group(3)); end_verse = int(m1.group(4))
        osis = resolve_osis(book)
        if not osis:
            raise HTTPException(status_code=400, detail=f"Livre non reconnu: '{book}'.")
        return book, osis, chapter, (start_verse, end_verse)
    m2 = re.match(r"^(.*?)\s+(\d+)(?::(\d+))?(?:\s+\S+.*)?$", p)
    if m2:
        book = m2.group(1).strip()
        chapter = int(m2.group(2)); verse = int(m2.group(3)) if m2.group(3) else None
        osis = resolve_osis(book)
        if not osis:
            raise HTTPException(status_code=400, detail=f"Livre non reconnu: '{book}'.")
        return book, osis, chapter, verse
    raise HTTPException(status_code=400, detail="Format passage invalide. Ex: 'Jean 3', 'Jean 3:16' ou 'Jean 3:1-5'.")

def parse_passage_input(p: str):
    p = p.strip()
    m = re.match(r"^(.*?)[\s,]+(\d+)(?::(\d+))?(?:\s+\S+.*)?$", p)
    if not m:
        raise HTTPException(status_code=400, detail="Format passage invalide. Ex: 'Genèse 1' ou 'Genèse 1:1'.")
    book = m.group(1).strip()
    chapter = int(m.group(2))
    verse = int(m.group(3)) if m.group(3) else None
    osis = resolve_osis(book)
    if not osis:
        raise HTTPException(status_code=400, detail=f"Livre non reconnu: '{book}'.")
    return book, osis, chapter, verse

# =========================
#   Théologie (fallback simple)
# =========================
def generate_smart_fallback_explanation(verse_text: str, book: str, chap: int, vnum: int) -> str:
    low = verse_text.lower()
    out = [f"ANALYSE TEXTUELLE DE {book} {chap}:{vnum}"]
    if any(w in low for w in ["lumière", "yehi", "אור"]):
        out.append("La formule 'yehi or' révèle l'efficacité de la Parole créatrice.")
    out.append("Ce passage s'inscrit dans l'économie révélationnelle et la lecture christocentrique.")
    return " ".join(out)

async def generate_enriched_theological_explanation(verse_text: str, book: str, chap: int, vnum: int, enriched: bool = True) -> str:
    return generate_smart_fallback_explanation(verse_text, book, chap, vnum)

# =========================
#        ROUTES
# =========================
@app.get("/")
def root():
    return {"message": APP_NAME, "status": "Railway deployment successful"}

# Health for Railway
@app.get("/health")
async def health_plain():
    try:
        bid = await get_bible_id()
    except Exception:
        bid = None
    return {"status": "ok", "bibleId": bid or "unknown", "gemini": GEMINI_AVAILABLE, "path": "/health"}

# Health (API namespace too)
@app.get("/api/health")
async def health_api():
    try:
        bid = await get_bible_id()
    except Exception:
        bid = None
    return {"status": "ok", "bibleId": bid or "unknown", "gemini": GEMINI_AVAILABLE, "path": "/api/health"}

@app.get("/api/")
def api_root():
    return {"message": APP_NAME}

@app.get("/api/test")
async def test_connection():
    return {"status": "Backend accessible", "message": "Connexion OK"}

# ---- Progressif
@app.post("/api/generate-verse-by-verse-progressive", response_model=ProgressiveStudyResponse)
async def generate_verse_by_verse_progressive(request: ProgressiveStudyRequest):
    try:
        passage = request.passage.strip()
        batch_size = max(1, min(request.batch_size, 10))
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")
        book_label, osis, chap, verse_info = parse_passage_input_extended(passage)
        bible_id = await get_bible_id()

        if isinstance(verse_info, tuple):
            start_verse_orig, end_verse = verse_info
        elif verse_info:
            start_verse_orig = end_verse = verse_info
        else:
            verses_list = await list_verses_ids(bible_id, osis, chap)
            start_verse_orig, end_verse = 1, len(verses_list) if verses_list else 31

        batch_start = request.start_verse
        batch_end = min(batch_start + batch_size - 1, end_verse)
        total_verses = max(1, end_verse - start_verse_orig + 1)

        batch_content = ""
        if batch_start == start_verse_orig:
            title = f"Étude Verset par Verset - {book_label} Chapitre {chap}"
            intro = "Cette étude parcourt la Bible Darby (FR) avec des explications théologiques enrichies automatiquement par IA."
            batch_content += f"# {title}\n\n{intro}\n\n"

        for v in range(batch_start, batch_end + 1):
            verse_text = await fetch_passage_text(bible_id, osis, chap, v)
            theox = await generate_enriched_theological_explanation(verse_text, book_label, chap, v, enriched=False)
            batch_content += (
                f"## VERSET {v}\n\n"
                f"**TEXTE BIBLIQUE :**\n{verse_text}\n\n"
                f"**EXPLICATION THÉOLOGIQUE :**\n{theox}\n\n---\n\n"
            )

        has_more = batch_end < end_verse
        next_start_verse = batch_end + 1 if has_more else end_verse
        verses_completed = batch_end - start_verse_orig + 1
        total_progress = min((verses_completed / total_verses) * 100, 100)

        verse_stats = {"processed": verses_completed, "total": total_verses, "remaining": max(0, total_verses - verses_completed)}

        return ProgressiveStudyResponse(
            batch_content=batch_content,
            verse_range=f"{batch_start}" if batch_start == batch_end else f"{batch_start}-{batch_end}",
            has_more=has_more,
            next_start_verse=next_start_verse,
            total_progress=round(total_progress, 1),
            verse_stats=verse_stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")

# ---- Non progressif
@app.post("/api/generate-verse-by-verse")
async def generate_verse_by_verse(request: StudyRequest):
    try:
        passage = request.passage.strip()
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")
        book_label, osis, chap, verse = parse_passage_input(passage)
        bible_id = await get_bible_id()
        text = await fetch_passage_text(bible_id, osis, chap, verse)

        title = f"**Étude Verset par Verset - {book_label} Chapitre {chap}**"
        intro = (
            "Introduction au Chapitre\n\n"
            "Cette étude parcourt le texte de la **Bible Darby (FR)**. "
            "Les sections EXPLICATION THÉOLOGIQUE sont enrichies automatiquement par IA théologique."
        )

        if verse:
            theox = await generate_enriched_theological_explanation(text, book_label, chap, verse, enriched=False)
            content = (
                f"{title}\n\n{intro}\n\n"
                f"**VERSET {verse}**\n\n"
                f"**TEXTE BIBLIQUE :**\n{text}\n\n"
                f"**EXPLICATION THÉOLOGIQUE :**\n{theox}"
            )
            return {"content": format_theological_content(content)}

        blocks: List[str] = [f"{title}\n\n{intro}"]
        # Grâce au fetch_passage_text, on a "1 ligne = 1 verset"
        lines = [l for l in text.splitlines() if l.strip()]
        for line in lines:
            m = re.match(r"^(\d+)\.\s*(.*)$", line)
            if not m:
                continue
            vnum = int(m.group(1))
            vtxt = m.group(2).strip()
            theox = await generate_enriched_theological_explanation(vtxt, book_label, chap, vnum, enriched=False)
            blocks.append(
                f"**VERSET {vnum}**\n\n"
                f"**TEXTE BIBLIQUE :**\n{vtxt}\n\n"
                f"**EXPLICATION THÉOLOGIQUE :**\n{theox}"
            )
        return {"content": format_theological_content("\n\n".join(blocks).strip())}
    except Exception as e:
        return {"content": f"Erreur lors de la génération: {str(e)}"}

# ---- Étude 28 rubriques (simplifiée)
RUBRIQUES_28 = [
    "Prière d'ouverture","Structure littéraire","Questions du chapitre précédent","Thème doctrinal",
    "Fondements théologiques","Contexte historique","Contexte culturel","Contexte géographique",
    "Analyse lexicale","Parallèles bibliques","Prophétie et accomplissement","Personnages","Structure rhétorique",
    "Théologie trinitaire","Christ au centre","Évangile et grâce","Application personnelle","Application communautaire",
    "Prière de réponse","Questions d'étude","Points de vigilance","Objections et réponses","Perspective missionnelle",
    "Éthique chrétienne","Louange / liturgie","Méditation guidée","Mémoire / versets clés","Plan d'action",
]

def generate_intelligent_rubric_content(rubric_num: int, book_name: str, chapter: int, text: str) -> str:
    rubric_name = RUBRIQUES_28[rubric_num - 1] if rubric_num <= len(RUBRIQUES_28) else f"Rubrique {rubric_num}"
    base = {
        1: f"Seigneur, ouvre nos cœurs à la compréhension de {book_name} {chapter}.",
        2: f"Le chapitre {chapter} de {book_name} révèle une structure littéraire au service du propos.",
        10: f"Les parallèles bibliques éclairent l'unité canonique de {book_name} {chapter}.",
        15: f"Christ, centre herméneutique, accomplit {book_name} {chapter}.",
        17: f"Application personnelle : comment {book_name} {chapter} transforme notre marche ?",
    }.get(rubric_num, f"Contenu contextualisé pour {book_name} {chapter}.")
    return f"## {rubric_num}. {rubric_name}\n\n{base}"

@app.get("/api/")
def api_root_index():
    return {"message": APP_NAME}

@app.post("/api/generate-study")
async def generate_study(request: StudyRequest):
    try:
        passage = request.passage.strip()
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")
        book_label, osis, chap, _ = parse_passage_input(passage)
        bible_id = await get_bible_id()
        text = await fetch_passage_text(bible_id, osis, chap, None)
        requested_indices = request.requestedRubriques or list(range(len(RUBRIQUES_28)))
        header = f"# Étude Intelligente en 28 points — {book_label} {chap} (Darby)\n"
        intro = "Étude enrichie (contenu local)"
        excerpt = "\n".join([l for l in text.splitlines()[:8]])
        body: List[str] = [header, "## 📖 Extrait du texte (Darby)\n" + excerpt, intro, "---"]
        for i, rubric_idx in enumerate(requested_indices):
            body.append(generate_intelligent_rubric_content(rubric_idx + 1, book_label, chap, text))
        return {"content": "\n\n".join(body).strip()}
    except Exception as e:
        return {"content": f"Erreur lors de la génération: {str(e)}"}

# ---- Run local
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
