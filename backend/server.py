
import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# -------------
# Mini "DB" de versets embarquée pour les tests
# -------------

GENESE_1 = {i: f"Texte du verset {i} (Genèse 1:{i})." for i in range(1, 32)}
PSAUMES_1 = {i: f"Heureux l'homme (Psaume 1:{i})." for i in range(1, 7)}

BIBLE = {
    ("Genese", 1): GENESE_1,
    ("Genèse", 1): GENESE_1,
    ("Psaumes", 1): PSAUMES_1,
}

# -------------
# Helpers
# -------------

def get_chapter_verses(passage: str) -> Dict[int, str]:
    """
    Accepte "Genese 1" ou "Genèse 1" ou "Psaumes 1".
    Retourne un dict {num_verset: texte}.
    """
    passage = (passage or "").strip()
    if ":" in passage:
        # on ignore le verset pour l'étude chapitre, on prendra les versets de tout le chapitre
        book, chap_verse = passage.split(maxsplit=1)
        if ":" in chap_verse:
            chap = int(chap_verse.split(":")[0])
        else:
            chap = int(chap_verse)
    else:
        parts = passage.split()
        if len(parts) >= 2:
            book = " ".join(parts[:-1])
            chap = int(parts[-1])
        else:
            return {}
    # normaliser quelques variantes simples
    key_candidates = [
        (book, chap),
        (book.replace("é", "e").replace("É", "E"), chap),
        (book.replace("e", "é").replace("E", "É"), chap),
    ]
    for k in key_candidates:
        if k in BIBLE:
            return BIBLE[k]
    return {}

def clamp(n: int, a: int, b: int) -> int:
    return max(a, min(b, n))

def build_local_explanation(book: str, chapter: int, verse_num: int, target_chars_per_verse: int) -> str:
    """Génère une courte explication locale en fonction du budget de caractères par verset."""
    base = (
        f"Analyse du verset {verse_num} de {book} {chapter}. "
        "Contexte: création/poésie/prose selon le passage. "
        "Théologiquement: le texte révèle la souveraineté de Dieu, la bonté de la création et la vocation humaine. "
        "Application: cultiver la foi, l'obéissance et la contemplation dans la vie quotidienne."
    )
    # Ajuster la longueur en répétant/écourtant proprement
    target = clamp(target_chars_per_verse, 60, 600)
    if len(base) < target:
        # étire en ajoutant des nuances
        addon = (
            " Lexicalement: remarquer les mots clés, la structure, et les parallèles canoniques. "
            " Spirituellement: inviter à la prière et à la louange."
        )
        s = base
        while len(s) + len(addon) < target:
            s += addon
        return s[:target].rstrip() + "."
    else:
        return base[:target].rstrip() + "."

def distribute_budget(total_chars: int, count: int) -> int:
    """Budget par verset. On donne un petit bonus pour ne pas être trop sec aux petits budgets."""
    if count <= 0:
        return 120
    # boost léger pour éviter un rendu trop court
    bonus = 1.4 if total_chars <= 600 else 1.2 if total_chars <= 1600 else 1.1
    per = int((total_chars * bonus) / count)
    return clamp(per, 60, 600)

def format_block(book: str, chapter: int, vnum: int, vtext: str, explanation: str) -> str:
    return (
        f"VERSET {vnum}\n\n"
        f"TEXTE BIBLIQUE :\n{vtext}\n\n"
        f"EXPLICATION THÉOLOGIQUE :\n{explanation}\n\n"
    )

def build_study_content(passage: str, enriched: bool, target_chars: int) -> str:
    verses = get_chapter_verses(passage)
    if not verses:
        return "Étude Verset par Verset\n\n(aucun verset trouvé pour ce passage)"
    # récupérer book & chapter depuis le passage
    parts = passage.split()
    book = " ".join(parts[:-1])
    chapter = int(parts[-1].split(":")[0]) if ":" in parts[-1] else int(parts[-1])
    nums = sorted(verses.keys())
    per_verse_budget = distribute_budget(target_chars or 500, len(nums)) if enriched else 0

    blocks = []
    # Introduction simple
    blocks.append(f"Étude Verset par Verset - {book} {chapter}\n")

    for n in nums:
        vtext = verses[n]
        if enriched:
            exp = build_local_explanation(book, chapter, n, per_verse_budget)
        else:
            exp = "Analyse courte. (Activez enriched=true pour un commentaire développé.)"
        blocks.append(format_block(book, chapter, n, vtext, exp))
    return "\n".join(blocks).strip() + "\n"

# -------------
# (Optionnel) Gemini — mock simple si GEMINI_API_KEY non défini
# -------------

def gemini_enabled() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))

# -------------
# FastAPI
# -------------

app = FastAPI(title="Étude8 Bible API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VerseRequest(BaseModel):
    passage: str = Field(..., examples=["Genese 1"])
    version: Optional[str] = "LSG"
    enriched: Optional[bool] = False
    target_chars: Optional[int] = Field(500, ge=100, le=5000)

class ProgressiveRequest(BaseModel):
    passage: str
    batch_size: int = Field(5, ge=1, le=20)
    start_verse: int = Field(1, ge=1)
    priority_mode: Optional[bool] = False
    enriched: Optional[bool] = False
    target_chars: Optional[int] = Field(500, ge=100, le=5000)

@app.get("/health")
def health_root():
    return {"status": "healthy", "message": "Railway backend operational"}

@app.get("/api/health")
def api_health():
    return {
        "status": "ok",
        "bibleId": "a93a92589195411f-01",
        "gemini": gemini_enabled(),
        "path": "/api/health",
    }

@app.post("/api/generate-verse-by-verse")
def generate_verse_by_verse(req: VerseRequest = Body(...)) -> Dict[str, Any]:
    # Si Gemini est présent et enriched, on pourrait appeler le modèle ici.
    # Pour garantir un rendu complet même sans Gemini, on fait toujours le fallback local.
    content = build_study_content(req.passage, bool(req.enriched), int(req.target_chars or 500))
    return {"content": content}

@app.post("/api/generate-verse-by-verse-progressive")
def generate_verse_by_verse_progressive(req: ProgressiveRequest = Body(...)) -> Dict[str, Any]:
    verses = get_chapter_verses(req.passage)
    if not verses:
        return {
            "batch_content": "",
            "verse_range": None,
            "has_more": False,
            "next_start_verse": None,
            "total_progress": 0.0,
            "verse_stats": {"processed": 0, "total": 0, "remaining": 0},
        }
    parts = req.passage.split()
    book = " ".join(parts[:-1])
    chapter = int(parts[-1].split(":")[0]) if ":" in parts[-1] else int(parts[-1])

    all_nums = sorted(verses.keys())
    total = len(all_nums)

    start = req.start_verse
    end = min(start + req.batch_size - 1, all_nums[-1])

    batch_nums = [n for n in all_nums if start <= n <= end]
    per_verse_budget = distribute_budget(req.target_chars or 500, total) if req.enriched else 0

    blocks = []
    for n in batch_nums:
        vtext = verses[n]
        if req.enriched:
            exp = build_local_explanation(book, chapter, n, per_verse_budget)
        else:
            exp = "Analyse courte. (Activez enriched=true pour un commentaire développé.)"
        blocks.append(format_block(book, chapter, n, vtext, exp))

    processed = end
    remaining = total - end
    total_progress = round((processed / total) * 100, 1)

    return {
        "batch_content": "\n".join(blocks).strip() + ("\n" if blocks else ""),
        "verse_range": f"{start}-{end}",
        "has_more": end < all_nums[-1],
        "next_start_verse": end + 1 if end < all_nums[-1] else None,
        "total_progress": total_progress,
        "verse_stats": {"processed": end, "total": total, "remaining": remaining},
    }
