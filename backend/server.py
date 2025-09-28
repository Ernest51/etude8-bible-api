# server.py
import os
import math
from typing import Optional, List, Dict, Any, Tuple

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# ---------- Optional Gemini wiring ----------
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() in {"1", "true", "yes", "on"}
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
gemini = None
if USE_GEMINI and GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini = genai
    except Exception as e:
        # If import/config fails, fall back to local enrichment
        gemini = None
        USE_GEMINI = False

# ---------- App ----------
app = FastAPI(title="Étude8 Bible API", version="1.1.0")

# CORS: allow all (adjust if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helpers & Static Data ----------
FALLBACK_TOTAL_VERSES = int(os.getenv("DEFAULT_VERSE_FALLBACK", "20"))
BIBLE_ID = os.getenv("BIBLE_ID", "a93a92589195411f-01")
VERSE_PROVIDER = os.getenv("VERSE_PROVIDER", "simulated").lower()  # internal | simulated

# Minimal verse count map (extend as needed)
TOTAL_VERSES_MAP = {
    ("Genèse", 1): 31,
    ("Genese", 1): 31,   # without accent for robustness
    ("Psaumes", 1): 6,
    ("Psaume", 1): 6,
}

# Accept a few common French book aliases
BOOK_ALIASES = {
    "genèse": "Genèse",
    "genese": "Genèse",
    "psaumes": "Psaumes",
    "psaume": "Psaumes",
}

def normalize_book(name: str) -> str:
    k = name.strip().lower()
    return BOOK_ALIASES.get(k, name).strip()

def parse_passage(passage: str) -> Tuple[str, int, Optional[int]]:
    """
    Accepts e.g. "Genèse 1", "Genese 1", "Genèse 1:5".
    Returns (book, chapter, verse|None).
    """
    s = (passage or "").strip()
    if not s:
        return ("", 0, None)
    # Split on last space to separate book and chapter/verse
    parts = s.rsplit(" ", 1)
    if len(parts) == 1:
        return (normalize_book(parts[0]), 1, None)
    book = normalize_book(parts[0])
    right = parts[1]
    if ":" in right:
        ch, vs = right.split(":", 1)
        try:
            return (book, int(ch), int(vs))
        except:
            return (book, int(ch) if ch.isdigit() else 1, None)
    else:
        try:
            return (book, int(right), None)
        except:
            return (book, 1, None)

def get_total_verses(book: str, chapter: int) -> int:
    return TOTAL_VERSES_MAP.get((book, chapter), FALLBACK_TOTAL_VERSES)

# ----- Verse text provider ----------------------------------------------------
# TODO: If you have a real internal provider, replace fetch_verse_text()
# with a call to your database/API when VERSE_PROVIDER == "internal".
def fetch_verse_text(book: str, chapter: int, verse: int) -> str:
    if VERSE_PROVIDER == "internal":
        # >>> Implement your internal lookup here <<<
        # Example:
        # return my_service.get_darby_text(book, chapter, verse)
        pass
    # Simulated minimal text (keeps structure predictable for your frontend)
    return f"[{verse}] (Texte simulé) {book} {chapter}:{verse} — contenu du verset."

# ----- Enrichment logic -------------------------------------------------------
def gemini_enrich(prompt: str, target_chars: int) -> Optional[str]:
    if not (USE_GEMINI and gemini and GEMINI_API_KEY):
        return None
    try:
        # Use a light model if available; fall back to generic
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        model = gemini.GenerativeModel(model_name)
        guidance = (
            "Rédige en français un commentaire théologique pastoral, solide mais concis. "
            "Structure ta réponse en 3 segments courts: "
            "ANALYSE TEXTUELLE • IMPLICATIONS DOGMATIQUES • APPLICATION PASTORALE. "
            f"Vise environ {target_chars} caractères au total."
        )
        full_prompt = guidance + "\n\n" + prompt
        resp = model.generate_content(full_prompt)
        if hasattr(resp, "text") and resp.text:
            # Trim to roughly target_chars ±25%
            txt = resp.text.strip()
            if len(txt) > int(target_chars * 1.25):
                return txt[: int(target_chars * 1.25)].rsplit(" ", 1)[0] + "…"
            return txt
    except Exception:
        return None
    return None

def local_enrich(book: str, chapter: int, verse: int, target_chars: int) -> str:
    """
    Deterministic enrichment that scales with target_chars.
    500: bref — ~3-4 phrases
    1500: moyen — ~6-8 phrases
    2500: développé — ~10-12 phrases
    """
    # Decide number of sentences from target
    if target_chars <= 600:
        n = 4
    elif target_chars <= 1700:
        n = 8
    else:
        n = 12

    blocks = [
        f"ANALYSE TEXTUELLE DE {book} {chapter}:{verse} – le verset est replacé dans son contexte littéraire et narratif, "
        "avec attention au vocabulaire source et aux parallèles immédiats.",
        "ANALYSE LEXICALE : référencement des mots-clés (hébreu/grec) de base et portée sémantique dans le passage.",
        "IMPLICATIONS DOGMATIQUES : doctrines de la création, de la providence, du péché et de la rédemption selon la pertinence du verset.",
        "CHRISTOCENTRISME : la lecture trouve son accomplissement dans la personne et l’œuvre du Christ dans l’unité canonique.",
        "ÉCONOMIE DU SALUT : articulation entre révélation progressive, alliance et vie de l’Église.",
        "CONSENSUS PATRUM : brève note patristique/réformée quand utile, évitant l’anachronisme.",
        "DIMENSION ÉTHIQUE : implications pour la sagesse, la sainteté et la justice dans la vie quotidienne.",
        "APPLICATION PASTORALE : pistes de méditation, prière et obéissance joyeuse.",
        "DISCERNEMENT : rappeler la tension déjà/pas-encore et les limites de la spéculation.",
        "MISSION : retombées communautaires et témoignage discret mais clair.",
        "ESPÉRANCE : encouragement à la persévérance et à la louange.",
        "SYNTHÈSE : une phrase de conclusion brève et mémorisable."
    ]
    text = " ".join(blocks[:n])
    # Gently trim/expand to approximate target size
    if len(text) > target_chars * 1.15:
        text = text[: int(target_chars * 1.1)].rsplit(" ", 1)[0] + "…"
    return text

def build_verse_block(book: str, chapter: int, verse: int, enriched: bool, target_chars: int) -> str:
    verse_text = fetch_verse_text(book, chapter, verse)
    block = []
    block.append(f"VERSET {verse}")
    block.append("")
    block.append("TEXTE BIBLIQUE :")
    block.append(verse_text)
    if enriched:
        block.append("")
        block.append("EXPLICATION THÉOLOGIQUE :")
        # Try Gemini; otherwise local
        if USE_GEMINI and gemini:
            prompt = f"{book} {chapter}:{verse} — texte: « {verse_text} ». Donne un commentaire structuré."
            enriched_text = gemini_enrich(prompt, target_chars=max(300, target_chars // 2))
            if not enriched_text:
                enriched_text = local_enrich(book, chapter, verse, target_chars=max(300, target_chars // 2))
        else:
            enriched_text = local_enrich(book, chapter, verse, target_chars=max(300, target_chars // 2))
        block.append(enriched_text)
    block.append("")
    return "\n".join(block)

def build_full_content(book: str, chapter: int, total_verses: int, enriched: bool, target_chars: int) -> str:
    header = []
    header.append(f"Étude Verset par Verset - {book} Chapitre {chapter}")
    header.append("")
    header.append("Introduction au Chapitre")
    header.append("")
    header.append("Cette étude parcourt le texte biblique avec des explications théologiques proportionnées à la longueur choisie.")
    header.append("")
    parts = ["\n".join(header)]

    # Distribute a per-verse enrichment budget
    # Keep a portion for the intro and natural variation
    per_verse_chars = max(200, int(target_chars / max(1, total_verses) * 0.9))

    for v in range(1, total_verses + 1):
        parts.append(build_verse_block(book, chapter, v, enriched=enriched, target_chars=per_verse_chars))

    return "\n".join(parts).strip() + "\n"

# ---------- Pydantic models ----------
class VerseRequest(BaseModel):
    passage: str = Field(..., description="Ex: 'Genèse 1' ou 'Genèse 1:5'")
    version: Optional[str] = Field(default="LSG")
    enriched: Optional[bool] = Field(default=False)
    target_chars: Optional[int] = Field(default=500, description="500|1500|2500")
    tokens: Optional[int] = Field(default=None, description="compat: mappé vers target_chars")

class VerseProgressiveRequest(BaseModel):
    passage: str
    version: Optional[str] = "LSG"
    batch_size: Optional[int] = Field(default=5, ge=1, le=50)
    start_verse: Optional[int] = Field(default=1, ge=1)
    priority_mode: Optional[bool] = False
    enriched: Optional[bool] = False
    target_chars: Optional[int] = 500
    tokens: Optional[int] = None

class StudyRequest(BaseModel):
    passage: str
    version: Optional[str] = "LSG"
    tokens: Optional[int] = 500
    enriched: Optional[bool] = True
    target_chars: Optional[int] = 500

# ---------- Health ----------
@app.get("/health")
def health_root():
    return {"status": "healthy", "message": "Railway backend operational"}

@app.get("/api/health")
def api_health():
    path = "/api/health"
    return {"status": "ok", "bibleId": BIBLE_ID, "gemini": bool(gemini), "path": path}

# ---------- Core endpoints ----------
def normalize_target_chars(tc: Optional[int], tokens: Optional[int]) -> int:
    # Map tokens/target to nearest of {500, 1500, 2500}
    if tc is None and tokens is not None:
        tc = tokens
    if tc is None:
        return 500
    if tc <= 700:
        return 500
    if tc <= 2000:
        return 1500
    return 2500

@app.post("/api/generate-verse-by-verse")
def generate_verse_by_verse(req: VerseRequest):
    book, chapter, verse = parse_passage(req.passage)
    if not book or not chapter:
        return {"content": "Passage invalide."}
    total = get_total_verses(book, chapter)
    target = normalize_target_chars(req.target_chars, req.tokens)
    enriched = bool(req.enriched)

    if verse:
        content = build_verse_block(book, chapter, verse, enriched=enriched, target_chars=target)
        return {"content": content}
    else:
        content = build_full_content(book, chapter, total, enriched=enriched, target_chars=target)
        return {"content": content}

@app.post("/api/generate-verse-by-verse-progressive")
def generate_verse_by_verse_progressive(req: VerseProgressiveRequest):
    book, chapter, verse = parse_passage(req.passage)
    total = get_total_verses(book, chapter)
    start = max(1, int(req.start_verse or 1))
    batch = max(1, min(int(req.batch_size or 5), 50))
    stop = min(total, start + batch - 1)
    target = normalize_target_chars(req.target_chars, req.tokens)
    enriched = bool(req.enriched)

    # Build current batch
    blocks = []
    for v in range(start, stop + 1):
        blocks.append(build_verse_block(book, chapter, v, enriched=enriched, target_chars=target))
    batch_content = "\n".join(blocks).strip() + "\n" if blocks else ""

    has_more = stop < total
    next_start = stop + 1 if has_more else None
    processed = stop - start + 1 if stop >= start else 0
    total_progress = round(processed / max(1, total) * 100, 1)

    return {
        "batch_content": batch_content,
        "verse_range": f"{start}-{stop}" if processed else None,
        "has_more": has_more,
        "next_start_verse": next_start,
        "total_progress": total_progress,
        "verse_stats": {"processed": processed, "total": total, "remaining": max(0, total - stop)},
    }

@app.post("/api/generate-study")
def generate_study(req: StudyRequest):
    # For now, generate the same content as full chapter with a heavier per-verse commentary
    book, chapter, verse = parse_passage(req.passage)
    total = get_total_verses(book, chapter)
    target = normalize_target_chars(req.target_chars, req.tokens)
    enriched = bool(req.enriched if req.enriched is not None else True)
    content = build_full_content(book, chapter, total, enriched=enriched, target_chars=target)
    # Prepend a simple header for 28-point study (structure can be extended)
    header = [
        f"# Étude structurée — {book} {chapter}",
        "",
        "Cette étude synthétise 28 axes (doctrine, contexte, application, mission, etc.) "
        "et adapte la densité des commentaires à la longueur sélectionnée.",
        "",
    ]
    return {"content": "\n".join(header) + content}

# ---------- Legacy aliases (kept for your frontend fallbacks) ----------
@app.post("/api/g_verse_progressive")
def alias_progressive(req: VerseProgressiveRequest):
    return generate_verse_by_verse_progressive(req)

@app.post("/api/g_te-verse-by-verse")
def alias_verse(req: VerseRequest):
    return generate_verse_by_verse(req)

@app.post("/api/g_study_28")
def alias_study(req: StudyRequest):
    return generate_study(req)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
