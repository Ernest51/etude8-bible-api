# -*- coding: utf-8 -*-
import os
import math
from typing import List, Optional, Tuple

from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# =============================
# Config & Flags
# =============================
APP_NAME = "Étude8 Bible API"
BIBLE_ID = "a93a92589195411f-01"  # conservé pour compat avec tes checks
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_OK = bool(GEMINI_API_KEY)

# =============================
# Minimal Bible store (Genèse 1 & Psaumes 1) pour tests
# Remplace/branche ici sur ta source réelle au besoin.
# =============================
STATIC_BIBLE = {
    ("Genese", 1): [
        "Au commencement Dieu créa les cieux et la terre.",
        "Et la terre était désolation et vide, et il y avait des ténèbres sur la face de l’abîme. Et l’Esprit de Dieu planait sur la face des eaux.",
        "Et Dieu dit : Que la lumière soit. Et la lumière fut.",
        "Et Dieu vit la lumière, qu’elle était bonne ; et Dieu sépara la lumière d’avec les ténèbres.",
        "Et Dieu appela la lumière Jour ; et les ténèbres, il les appela Nuit. Et il y eut soir, et il y eut matin : – premier jour.",
        "Et Dieu dit : Qu’il y ait une étendue entre les eaux, et qu’elle sépare les eaux d’avec les eaux.",
        "Et Dieu fit l’étendue, et sépara les eaux qui sont au-dessous de l’étendue d’avec les eaux qui sont au-dessus de l’étendue. Et il fut ainsi.",
        "Et Dieu appela l’étendue Cieux. Et il y eut soir, et il y eut matin : – second jour.",
        "Et Dieu dit : Que les eaux [qui sont] au-dessous des cieux se rassemblent en un lieu, et que le sec paraisse. Et il fut ainsi.",
        "Et Dieu appela le sec Terre, et le rassemblement des eaux, il l’appela Mers. Et Dieu vit que cela était bon.",
        "Et Dieu dit : Que la terre produise l’herbe, la plante portant de la semence, l’arbre fruitier produisant du fruit selon son espèce, ayant sa semence en soi sur la terre. Et il fut ainsi.",
        "Et la terre produisit l’herbe, la plante portant de la semence selon son espèce, et l’arbre produisant du fruit ayant sa semence en soi selon son’espèce. Et Dieu vit que cela était bon.",
        "Et il y eut soir, et il y eut matin : – troisième jour.",
        "Et Dieu dit : Qu’il y ait des luminaires dans l’étendue des cieux pour séparer le jour d’avec la nuit, et qu’ils soient pour signes et pour saisons [déterminées] et pour jours et pour années ;",
        "et qu’ils soient pour luminaires dans l’étendue des cieux pour donner de la lumière sur la terre. Et il fut ainsi.",
        "Et Dieu fit les deux grands luminaires, le grand luminaire pour dominer sur le jour, et le petit luminaire pour dominer sur la nuit ; et les étoiles.",
        "Et Dieu les plaça dans l’étendue des cieux pour donner de la lumière sur la terre,",
        "et pour dominer de jour et de nuit, et pour séparer la lumière d’avec les ténèbres. Et Dieu vit que cela était bon.",
        "Et il y eut soir, et il y eut matin : – quatrième jour.",
        "Et Dieu dit : Que les eaux foisonnent d’un fourmillement d’êtres vivants, et que les oiseaux volent au-dessus de la terre devant l’étendue des cieux.",
        "Et Dieu créa les grands animaux des eaux, et tout être vivant qui se meut, dont les eaux fourmillent, selon leurs espèces, et tout oiseau ailé selon son espèce. Et Dieu vit que cela était bon.",
        "Et Dieu les bénit, disant : Fructifiez, et multipliez, et remplissez les eaux dans les mers, et que l’oiseau multiplie sur la terre.",
        "Et il y eut soir, et il y eut matin : – cinquième jour.",
        "Et Dieu dit : Que la terre produise des êtres vivants selon leur espèce, le bétail, et [tout] ce qui rampe, et les bêtes de la terre selon leur espèce. Et il fut ainsi.",
        "Et Dieu fit les bêtes de la terre selon leur espèce, et le bétail selon son espèce, et tout reptile du sol selon son espèce. Et Dieu vit que cela était bon.",
        "Et Dieu dit : Faisons l’homme à notre image, selon notre ressemblance, et qu’ils dominent sur les poissons de la mer, et sur les oiseaux des cieux, et sur le bétail, et sur toute la terre, et sur tout [animal] rampant qui rampe sur la terre.",
        "Et Dieu créa l’homme à son image ; il le créa à l’image de Dieu ; il les créa mâle et femelle.",
        "Et Dieu les bénit ; et Dieu leur dit : Fructifiez, et multipliez, et remplissez la terre et l’assujettissez ; et dominez sur les poissons de la mer, et sur les oiseaux des cieux, et sur tout être vivant qui se meut sur la terre.",
        "Et Dieu dit : Voici, je vous ai donné toute plante portant semence, qui est sur la face de toute la terre, et tout arbre dans lequel il y a un fruit d’arbre, portant semence ; [cela] vous sera pour nourriture ;",
        "et à tout animal de la terre, et à tout oiseau des cieux, et à tout ce qui rampe sur la terre, qui a en soi une âme vivante, [j’ai donné] toute plante verte pour nourriture. Et il fut ainsi.",
        "Et Dieu vit tout ce qu’il avait fait, et voici, cela était très bon. Et il y eut soir, et il y eut matin : – le sixième jour.",
    ],
    ("Psaumes", 1): [
        "Heureux l’homme qui ne marche pas dans le conseil des méchants, qui ne s’arrête pas dans la voie des pécheurs, et qui ne s’assied pas au siège des moqueurs,",
        "mais qui trouve son plaisir dans la loi de l’Éternel, et qui médite sa loi jour et nuit !",
        "Il sera comme un arbre planté près des ruisseaux d’eau, qui donne son fruit en sa saison, et dont la feuille ne se flétrit point ; et tout ce qu’il fait réussit.",
        "Il n’en est pas ainsi des méchants : mais ils sont comme la bale que le vent chasse.",
        "C’est pourquoi les méchants ne subsisteront pas dans le jugement, ni les pécheurs dans l’assemblée des justes.",
        "Car l’Éternel connaît la voie des justes, mais la voie des méchants périra.",
    ],
}

# =============================
# Helpers
# =============================
def parse_passage(p: str) -> Tuple[str, int]:
    """
    Transforme 'Genese 1' ou 'Psaumes 1' en (book, chapter).
    """
    raw = (p or "").strip()
    if not raw:
        return ("", 0)
    parts = raw.split()
    if len(parts) < 2:
        return (raw, 1)
    try:
        ch = int(parts[-1])
        book = " ".join(parts[:-1])
        return (book, ch)
    except ValueError:
        # aucun chapitre détecté → 1 par défaut
        return (raw, 1)

def normalize_title(p: str) -> str:
    b, c = parse_passage(p)
    return f"{b} {c}".strip()

def get_chapter_verses(passage: str, version: str = "LSG") -> List[Tuple[int, str]]:
    """
    Retourne [(num, texte), ...].
    Branche ici ta vraie source si besoin.
    """
    book, chap = parse_passage(passage)
    key = (book, chap)
    verses = STATIC_BIBLE.get(key, [])
    return [(i + 1, txt) for i, txt in enumerate(verses)]

def clamp_text(s: str, limit: int) -> str:
    s = (s or "").strip()
    if not limit or limit <= 0:
        return s
    return (s[:limit] + "…") if len(s) > limit else s

def fallback_theological_note(passage: str, num: int, text: str, limit: int = 180) -> str:
    base = (
        f"ANALYSE TEXTUELLE DE {passage}:{num} – "
        f"mouvement parole/acte/évaluation ; "
        f"un écho canonique et une implication pratique. "
        f"Le verset met en relief la parole efficace de Dieu et son dessein dans l'économie biblique."
    )
    return clamp_text(base, limit)

# =============================
# Gemini (optionnel)
# =============================
def try_import_gemini():
    if not GEMINI_OK:
        return None
    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception:
        return None

GEMINI_MODEL = try_import_gemini()

def enrich_with_gemini(passage: str, verse_num: int, verse_text: str, target_chars: int, version: str) -> str:
    if not GEMINI_MODEL:
        raise RuntimeError("Gemini indisponible")
    prompt = f"""Tu es un assistant théologique. En {max(80, target_chars)} caractères environ,
produis une brève explication pour {passage}:{verse_num} (version {version}).

TEXTE:
{verse_text}

Structure en 1–3 phrases, sans polémique :
- axe théologique / mouvement littéraire
- 1 note lexicale ou écho biblique
- 1 implication prière/vie
"""
    try:
        resp = GEMINI_MODEL.generate_content(prompt)
        txt = (resp.text or "").strip()
        return clamp_text(txt, target_chars or 200)
    except Exception as e:
        raise RuntimeError(str(e))

# =============================
# FastAPI App
# =============================
app = FastAPI(title=APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class VerseRequest(BaseModel):
    passage: str = Field(..., description="Ex: 'Genese 1'")
    version: Optional[str] = "LSG"
    enriched: Optional[bool] = False
    target_chars: Optional[int] = 0

class ProgressiveRequest(BaseModel):
    passage: str
    batch_size: int = 5
    start_verse: int = 1
    priority_mode: Optional[bool] = False
    enriched: Optional[bool] = False
    version: Optional[str] = "LSG"
    target_chars: Optional[int] = 0

# Routes Health
@app.get("/health")
def health_root():
    return {"status": "healthy", "message": "Railway backend operational"}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "bibleId": BIBLE_ID, "gemini": GEMINI_OK, "path": "/api/health"}

# Core builder
def build_content(passage: str, version: str, enriched: bool, target_chars: int) -> str:
    verses = get_chapter_verses(passage, version=version or "LSG")
    if not verses:
        return "Étude Verset par Verset\n\n(Aucun verset trouvé pour ce passage)"

    total = len(verses)
    per_verse = int((target_chars or 0) / total) if target_chars else 0

    out_lines: List[str] = []
    out_lines.append(f"Étude Verset par Verset - {normalize_title(passage)}\n")

    for num, verse_text in verses:
        out_lines.append(f"VERSET {num}\n")
        out_lines.append("TEXTE BIBLIQUE :")
        out_lines.append(f"[{num}] {verse_text}\n")

        out_lines.append("EXPLICATION THÉOLOGIQUE :")
        if enriched:
            try:
                if GEMINI_MODEL:
                    theo = enrich_with_gemini(passage, num, verse_text, per_verse or 180, version or "LSG")
                else:
                    # fallback local si pas de Gemini
                    theo = fallback_theological_note(passage, num, verse_text, limit=per_verse or 180)
            except Exception:
                theo = fallback_theological_note(passage, num, verse_text, limit=per_verse or 180)
        else:
            # sans enrichissement → ligne vide pour rester compatible
            theo = ""
        out_lines.append(theo if theo else "—")
        out_lines.append("\n---\n")

    return "\n".join(out_lines).rstrip() + "\n"

# Routes
@app.post("/api/generate-verse-by-verse")
async def generate_verse_by_verse(req: VerseRequest):
    content = build_content(
        passage=req.passage,
        version=req.version or "LSG",
        enriched=bool(req.enriched),
        target_chars=int(req.target_chars or 0),
    )
    return {"content": content}

@app.post("/api/generate-verse-by-verse-progressive")
async def generate_verse_by_verse_progressive(req: ProgressiveRequest):
    verses = get_chapter_verses(req.passage, version=req.version or "LSG")
    total = len(verses)
    if total == 0:
        return {
            "batch_content": "Aucun verset trouvé",
            "verse_range": None,
            "has_more": False,
            "next_start_verse": None,
            "total_progress": 0.0,
            "verse_stats": {"processed": 0, "total": 0, "remaining": 0},
        }

    start = max(1, int(req.start_verse or 1))
    size = max(1, int(req.batch_size or 5))
    end = min(total, start + size - 1)
    slice_verses = verses[start-1:end]

    # budget sur le batch
    per_verse = 0
    if req.enriched and req.target_chars:
        total_batches = math.ceil(total / size)
        batch_budget = int((req.target_chars or 0) / total_batches) if req.target_chars else 0
        per_verse = int(batch_budget / len(slice_verses)) if slice_verses else 0

    # construire le contenu du batch
    lines: List[str] = []
    for num, verse_text in slice_verses:
        lines.append(f"## VERSET {num}\n")
        lines.append("**TEXTE BIBLIQUE :**")
        lines.append(f"[{num}] {verse_text}\n")
        lines.append("**EXPLICATION THÉOLOGIQUE :**")
        if req.enriched:
            try:
                if GEMINI_MODEL:
                    theo = enrich_with_gemini(req.passage, num, verse_text, per_verse or 150, req.version or "LSG")
                else:
                    theo = fallback_theological_note(req.passage, num, verse_text, limit=per_verse or 150)
            except Exception:
                theo = fallback_theological_note(req.passage, num, verse_text, limit=per_verse or 150)
        else:
            theo = ""
        lines.append(theo if theo else "—")
        lines.append("\n---\n")

    batch_content = "\n".join(lines).rstrip() + "\n"
    has_more = end < total
    next_start = end + 1 if has_more else None
    total_progress = round(100.0 * end / total, 1)

    return {
        "batch_content": batch_content,
        "verse_range": f"{start}-{end}",
        "has_more": has_more,
        "next_start_verse": next_start,
        "total_progress": total_progress,
        "verse_stats": {"processed": end, "total": total, "remaining": total - end},
    }

# Uvicorn entry (Railway/Vercel)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
