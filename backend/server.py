import os
import re
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Config Bible API ---
BIBLE_ID = "a93a92589195411f-01"
BIBLE_API_URL = "https://api.scripture.api.bible/v1/bibles"
BIBLE_API_KEY = os.getenv("BIBLE_API_KEY", "demo")  # ⚠️ à remplacer

# --- Models ---
class PassageRequest(BaseModel):
    passage: str
    version: str | None = "LSG"
    enriched: bool | None = False
    target_chars: int | None = 500
    batch_size: int | None = None
    start_verse: int | None = None
    priority_mode: bool | None = False
    requestedRubriques: list[int] | None = None

# --- Helpers ---
def fetch_bible_text(passage: str) -> str:
    """
    Récupère le texte biblique brut depuis l’API scripture.api.bible
    """
    headers = {"api-key": BIBLE_API_KEY}
    url = f"{BIBLE_API_URL}/{BIBLE_ID}/passages/{passage}?content-type=text&include-verse-numbers=true"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return f"[Erreur API Bible] {r.text}"
    data = r.json()
    return data.get("data", {}).get("content", "")

def format_verses(raw_text: str, enriched=False, target_chars=500) -> str:
    """
    Nettoie et formate le texte : VERSET n, TEXTE BIBLIQUE, EXPLICATION THÉOLOGIQUE.
    Ajoute enrichissement simulé si demandé.
    """
    verses = re.split(r"\[(\d+)\]", raw_text)
    out = ["Étude Verset par Verset\n"]

    for i in range(1, len(verses), 2):
        num = verses[i]
        txt = verses[i+1].strip().replace("\n", " ")
        out.append(f"VERSET {num}\n")
        out.append("TEXTE BIBLIQUE :\n")
        out.append(txt + "\n")
        if enriched:
            exp = f"(Commentaire enrichi — longueur {target_chars} caractères pour le verset {num})"
            out.append("EXPLICATION THÉOLOGIQUE :\n")
            out.append(exp + "\n")

    return "\n".join(out)

# --- Routes ---
@app.get("/health")
async def root_health():
    return {"status": "healthy", "message": "Railway backend operational"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "bibleId": BIBLE_ID, "gemini": False, "path": "/api/health"}

@app.post("/api/generate-verse-by-verse")
async def generate_vbv(req: PassageRequest):
    raw_text = fetch_bible_text(req.passage)
    formatted = format_verses(raw_text, enriched=req.enriched, target_chars=req.target_chars)
    return {"content": formatted}

@app.post("/api/generate-verse-by-verse-progressive")
async def generate_vbv_progressive(req: PassageRequest):
    raw_text = fetch_bible_text(req.passage)
    formatted = format_verses(raw_text, enriched=req.enriched, target_chars=req.target_chars)

    # Pagination par batch_size
    all_lines = formatted.splitlines()
    verses = [i for i, l in enumerate(all_lines) if l.startswith("VERSET ")]
    start_idx = req.start_verse - 1 if req.start_verse else 0
    batch_size = req.batch_size or 5

    selected = verses[start_idx:start_idx+batch_size]
    if not selected:
        return {"verse_range": None, "batch_content": ""}

    start_line = selected[0]
    end_line = verses[min(start_idx+batch_size, len(verses)) - 1]
    batch_content = "\n".join(all_lines[start_line:end_line+10])  # extra 10 lines

    return {
        "verse_range": f"{req.start_verse}-{req.start_verse+batch_size-1}",
        "batch_content": batch_content
    }

@app.post("/api/generate-study")
async def generate_study(req: PassageRequest):
    # Simule l’étude en 28 rubriques enrichies
    rubriques = []
    for i in range(28):
        rubriques.append(f"Rubrique {i+1} ({req.target_chars} chars): contenu enrichi pour {req.passage}")
    return {"content": "\n\n".join(rubriques)}
