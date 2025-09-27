# backend/server.py
# API Bible Study (Darby) — avec contenu détaillé verset par verset et explications théologiques automatiques
# - Texte biblique via https://api.scripture.api.bible/v1
# - Étude "28 rubriques" + Verset/verset avec contenu théologique détaillé
# - Utilise ta bibliothèque locale si présente, sinon Gemini (si clé), sinon fallback
# - Renvoie toujours {"content": "..."} pour coller au front.

import os
import re
import unicodedata
from typing import Dict, List, Optional
from dotenv import load_dotenv

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ==== Chargement env ====
load_dotenv()

API_BASE = "https://api.scripture.api.bible/v1"
APP_NAME = "Bible Study API - Darby"
BIBLE_API_KEY = os.getenv("BIBLE_API_KEY", "")
PREFERRED_BIBLE_ID = os.getenv("BIBLE_ID", "a93a92589195411f-01")  # Darby FR
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY")

# ==== Bibliothèque locale riche (ta base) ====
try:
    from verse_by_verse_content import (
        get_verse_by_verse_content as vlib_chapter_dict,
        get_all_verses_for_chapter as vlib_all_verses,
    )
    VLIB_AVAILABLE = True
    print("✅ Local verse-by-verse library loaded")
except Exception:
    VLIB_AVAILABLE = False
    print("ℹ️ No local verse-by-verse library found")

# ==== Intégration Emergent / Gemini (optionnelle) ====
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    GEMINI_AVAILABLE = True
    print("✅ Emergent integrations loaded - Google Gemini Flash available")
except Exception:
    GEMINI_AVAILABLE = False
    print("ℹ️ Emergent integrations not available - using fallback mode")

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
    allow_origins=ALLOW_ORIGINS if _extra else ["*"],  # large en phase de test
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
#      SCHEMAS
# =========================
class StudyRequest(BaseModel):
    passage: str = Field(..., description="Ex: 'Nombres 2' ou 'Jean 3'")
    version: str = Field("", description="Ignoré (api.bible gère par bibleId).")
    tokens: int = Field(0, description="Ignoré (hérité du front).")
    model: str = Field("", description="Ignoré (hérité du front).")
    requestedRubriques: Optional[List[int]] = Field(
        None, description="Index des rubriques à produire (0..27). None = toutes."
    )

class ProgressiveStudyRequest(BaseModel):
    passage: str = Field(..., description="Passage biblique pour étude progressive")
    version: str = Field(default="LSG", description="Version de la Bible")
    batch_size: int = Field(default=5, description="Nombre de versets par batch")
    start_verse: int = Field(default=1, description="Verset de départ")

class ProgressiveStudyResponse(BaseModel):
    batch_content: str = Field(..., description="Contenu du batch actuel")
    verse_range: str = Field(..., description="Plage des versets traités")
    has_more: bool = Field(..., description="S'il y a encore des versets")
    next_start_verse: int = Field(..., description="Prochain verset")
    total_progress: float = Field(..., description="Pourcentage de progression total")

class VerseByVerseRequest(BaseModel):
    passage: str = Field(..., description="Ex: 'Genèse 1' ou 'Genèse 1:1'")
    version: str = Field("", description="Ignoré (api.bible).")


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
    """Formate le contenu théologique : retire les ** et nettoie."""
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
    content = content.replace('**', '').replace('*', '')
    content = re.sub(r'[ ]+', ' ', content)
    return content.strip()

def clean_plain_text(s: str) -> str:
    s = s.replace("**", "").replace("*", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()

BOOKS_FR_OSIS: Dict[str, str] = {
    # Pentateuque
    "genese": "GEN", "gen": "GEN",
    "exode": "EXO", "exo": "EXO",
    "levitique": "LEV", "lev": "LEV",
    "nombres": "NUM", "nom": "NUM", "nbr": "NUM", "nb": "NUM",
    "deuteronome": "DEU", "deut": "DEU", "dt": "DEU",
    # Historiques
    "josue": "JOS", "juges": "JDG", "ruth": "RUT",
    "1 samuel": "1SA", "2 samuel": "2SA",
    "1 rois": "1KI", "2 rois": "2KI",
    "1 chroniques": "1CH", "2 chroniques": "2CH",
    "esdras": "EZR", "nehemie": "NEH", "esther": "EST",
    # Poétiques
    "job": "JOB", "psaumes": "PSA", "psaume": "PSA", "ps": "PSA",
    "proverbes": "PRO", "prov": "PRO",
    "ecclesiaste": "ECC", "cantique des cantiques": "SNG", "cantique": "SNG",
    # Prophètes majeurs
    "esaie": "ISA", "jeremie": "JER", "lamentations": "LAM",
    "ezechiel": "EZK", "daniel": "DAN",
    # Prophètes mineurs
    "osee": "HOS", "joel": "JOL", "amos": "AMO", "abdi": "OBA",
    "jonas": "JON", "michee": "MIC", "nahum": "NAM", "habakuk": "HAB",
    "sophonie": "ZEP", "aggee": "HAG", "zacharie": "ZEC", "malachie": "MAL",
    # Évangiles & Actes
    "matthieu": "MAT", "marc": "MRK", "luc": "LUK", "jean": "JHN",
    "actes": "ACT",
    # Épîtres
    "romains": "ROM", "1 corinthiens": "1CO", "2 corinthiens": "2CO",
    "galates": "GAL", "ephesiens": "EPH", "philippiens": "PHP",
    "colossiens": "COL", "1 thessaloniciens": "1TH", "2 thessaloniciens": "2TH",
    "1 timothee": "1TI", "2 timothee": "2TI", "tite": "TIT", "philemon": "PHM",
    "hebreux": "HEB", "jacques": "JAS", "1 pierre": "1PE", "2 pierre": "2PE",
    "1 jean": "1JN", "2 jean": "2JN", "3 jean": "3JN", "jude": "JUD",
    # Apocalypse
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
_cached_bible_name: Optional[str] = None

async def get_bible_id() -> str:
    global _cached_bible_id, _cached_bible_name
    if _cached_bible_id:
        return _cached_bible_id

    if PREFERRED_BIBLE_ID:
        _cached_bible_id = PREFERRED_BIBLE_ID
        _cached_bible_name = "Darby (config)"
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
                _cached_bible_name = b.get("name")
                break
        if not _cached_bible_id:
            for b in lst:
                lang = (b.get("language") or {}).get("name", "")
                if "fr" in lang.lower() or "fra" in lang.lower():
                    _cached_bible_id = b.get("id")
                    _cached_bible_name = b.get("name")
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
        content = clean_plain_text(content)
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
    return clean_plain_text("\n".join(parts).strip())

# =========================
#   Parsing du passage
# =========================
def parse_passage_input_extended(p: str):
    """
    'Jean 3:1-5' -> ('Jean','JHN',3,(1,5))
    'Jean 3:16'  -> ('Jean','JHN',3,16)
    'Jean 3'     -> ('Jean','JHN',3,None)
    """
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
    """
    'Genèse 1'    -> ('Genèse', 1, None)
    'Genèse 1:3'  -> ('Genèse', 1, 3)
    """
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
#   Génération théologique
# =========================
async def generate_simple_theological_explanation(verse_text: str, book: str, chap: int, vnum: int) -> str:
    """Priorité: ta bibliothèque locale -> Gemini -> fallback."""
    # 1) Bibliothèque locale
    if VLIB_AVAILABLE:
        try:
            chap_dict = vlib_chapter_dict(book, chap) or {}
            entry = chap_dict.get(vnum)
            if entry and entry.get("explanation"):
                return format_theological_content(entry["explanation"])
        except Exception as e:
            print(f"VLIB miss for {book} {chap}:{vnum} -> {e}")

    # 2) Gemini si dispo
    if GEMINI_AVAILABLE and EMERGENT_LLM_KEY:
        try:
            chat = (
                LlmChat(
                    api_key=EMERGENT_LLM_KEY,
                    session_id=f"verse_{book}_{chap}_{vnum}",
                    system_message="Théologien expert : explications spécifiques, contextuelles, en français.",
                ).with_model("gemini", "gemini-2.0-flash")
            )
            prompt = f"""
Donne une explication théologique précise pour {book} {chap}:{vnum}.

TEXTE : {verse_text}

Exigences :
- 2–3 paragraphes concis (150–200 mots max)
- Spécifique à ce verset (pas générique)
- Contexte historique/culturel si pertinent
- Références internes à l'Écriture si utile
- Langage accessible mais solide
- Réponds UNIQUEMENT par l'explication"""
            resp = await chat.send_message(UserMessage(text=prompt))
            if resp and len(resp.strip()) > 50:
                return format_theological_content(resp.strip())
        except Exception as e:
            if any(k in str(e) for k in ("SSL", "TLS", "EOF")):
                pass

    # 3) Fallback court
    low = verse_text.lower()
    parts = []
    if book == "Genèse" and chap == 1 and vnum == 1:
        parts.append("Ce premier verset proclame la création ex nihilo et fonde l'autorité du Créateur sur toute réalité.")
    if "lumi" in low:
        parts.append("Le thème de la lumière manifeste la révélation et la vie procédant de Dieu (cf. Jean 1; 8:12).")
    if "parole" in low:
        parts.append("La création par la parole souligne la puissance efficace du Logos (Ps 33; Hé 11:3).")
    if not parts:
        parts.append(f"Ce verset, dans {book} {chap}, s'inscrit dans l'économie du salut et appelle à la foi et à l'obéissance.")
    return " ".join(parts)

# =========================
#   Génération "28 rubriques" (intelligente basique)
# =========================
RUBRIQUES_28 = [
    "Prière d'ouverture",
    "Structure littéraire",
    "Questions du chapitre précédent",
    "Thème doctrinal",
    "Fondements théologiques",
    "Contexte historique",
    "Contexte culturel",
    "Contexte géographique",
    "Analyse lexicale",
    "Parallèles bibliques",
    "Prophétie et accomplissement",
    "Personnages",
    "Structure rhétorique",
    "Théologie trinitaire",
    "Christ au centre",
    "Évangile et grâce",
    "Application personnelle",
    "Application communautaire",
    "Prière de réponse",
    "Questions d'étude",
    "Points de vigilance",
    "Objections et réponses",
    "Perspective missionnelle",
    "Éthique chrétienne",
    "Louange / liturgie",
    "Méditation guidée",
    "Mémoire / versets clés",
    "Plan d'action",
]

def generate_intelligent_rubric_content(rubric_num: int, book_name: str, chapter: int,
                                        text: str, historical_context: str = "", cross_refs = None) -> str:
    if cross_refs is None:
        cross_refs = []
    rubric_name = RUBRIQUES_28[rubric_num - 1] if rubric_num <= len(RUBRIQUES_28) else f"Rubrique {rubric_num}"
    base = {
        1: f"Seigneur, ouvre nos cœurs à la compréhension de {book_name} {chapter}. Que ton Esprit nous guide.",
        2: f"Le chapitre {chapter} de {book_name} révèle une structure qui sert le propos théologique de l'auteur.",
        4: f"Le thème doctrinal central de {book_name} {chapter} manifeste des vérités fondamentales sur Dieu.",
        6: f"Le contexte historique éclaire la situation des premiers auditeurs de {book_name} {chapter}.",
        10: f"Les parallèles bibliques enrichissent la lecture canonique de {book_name} {chapter}.",
        15: f"Christ se révèle au centre de {book_name} {chapter} comme accomplissement des promesses.",
        17: f"Application personnelle : comment {book_name} {chapter} transforme notre marche aujourd'hui ?",
    }.get(rubric_num, f"Contenu contextualisé pour {book_name} {chapter}.")
    out = f"## {rubric_num}. {rubric_name}\n\n{base}"
    if historical_context:
        out += f"\n\nContexte historique: {historical_context}"
    if cross_refs:
        ref_strings = []
        for ref in cross_refs[:3]:
            try:
                if getattr(ref, 'verse', None):
                    ref_strings.append(f"{ref.book} {ref.chapter}:{ref.verse}")
                else:
                    ref_strings.append(f"{ref.book} {ref.chapter}")
            except Exception:
                ref_strings.append(str(ref))
        if ref_strings:
            out += f"\n\nRéférences croisées: {', '.join(ref_strings)}"
    return out

# =========================
#        ROUTES
# =========================
@app.get("/api/")
def root():
    return {"message": APP_NAME}

@app.get("/api/test")
async def test_connection():
    return {"status": "Backend accessible", "message": "Connexion OK"}

@app.get("/api/health")
async def health():
    bid = None
    try:
        bid = await get_bible_id()
    except Exception:
        pass
    return {"status": "ok", "bibleId": bid or "unknown"}

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
            try:
                verses_list = await list_verses_ids(bible_id, osis, chap)
                start_verse_orig, end_verse = 1, len(verses_list)
            except Exception:
                start_verse_orig, end_verse = 1, 31

        batch_start = request.start_verse
        batch_end = min(batch_start + batch_size - 1, end_verse)

        batch_content = ""
        if batch_start == start_verse_orig:
            title = f"Étude Verset par Verset - {book_label} Chapitre {chap}"
            intro = "Cette étude parcourt la Bible Darby (FR). Les explications théologiques sont générées automatiquement."
            batch_content += f"# {title}\n\n{intro}\n\n"

        for v in range(batch_start, batch_end + 1):
            verse_text = await fetch_passage_text(bible_id, osis, chap, v)
            theox = await generate_simple_theological_explanation(verse_text, book_label, chap, v)
            theox = format_theological_content(theox)
            batch_content += (
                f"## VERSET {v}\n\n"
                f"**TEXTE BIBLIQUE :**\n{verse_text}\n\n"
                f"**EXPLICATION THÉOLOGIQUE :**\n{theox}\n\n---\n\n"
            )

        has_more = batch_end < end_verse
        next_start_verse = batch_end + 1 if has_more else end_verse
        total_verses = end_verse - start_verse_orig + 1
        verses_completed = batch_end - start_verse_orig + 1
        total_progress = min((verses_completed / total_verses) * 100, 100)

        return ProgressiveStudyResponse(
            batch_content=batch_content,
            verse_range=f"{batch_start}" if batch_start == batch_end else f"{batch_start}-{batch_end}",
            has_more=has_more,
            next_start_verse=next_start_verse,
            total_progress=round(total_progress, 1),
        )
    except Exception as e:
        print(f"❌ Erreur generate_verse_by_verse_progressive: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")

# ---- Verset par verset (non progressif)
@app.post("/api/generate-verse-by-verse")
async def generate_verse_by_verse(request: StudyRequest):
    try:
        passage = request.passage.strip()
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")
        base = await _generate_verse_by_verse_content(request)
        return base
    except Exception as e:
        print(f"❌ Erreur generate_verse_by_verse: {e}")
        return {"content": f"Erreur lors de la génération: {str(e)}"}

async def _generate_verse_by_verse_content(req: StudyRequest):
    book_label, osis, chap, verse = parse_passage_input(req.passage)
    bible_id = await get_bible_id()
    text = await fetch_passage_text(bible_id, osis, chap, verse)

    title = f"**Étude Verset par Verset - {book_label} Chapitre {chap}**"
    intro = (
        "Introduction au Chapitre\n\n"
        "Cette étude parcourt le texte de la **Bible Darby (FR)**. "
        "Les sections EXPLICATION THÉOLOGIQUE sont générées automatiquement."
    )

    if verse:
        theox = await generate_simple_theological_explanation(text, book_label, chap, verse)
        theox = format_theological_content(theox)
        content = (
            f"{title}\n\n{intro}\n\n"
            f"**VERSET {verse}**\n\n"
            f"**TEXTE BIBLIQUE :**\n{text}\n\n"
            f"**EXPLICATION THÉOLOGIQUE :**\n{theox}"
        )
        return {"content": format_theological_content(content)}

    # Chapitre entier
    blocks: List[str] = [f"{title}\n\n{intro}"]

    # Si ta bibliothèque locale est dispo, on l'utilise (texte + explications riches)
    if VLIB_AVAILABLE:
        try:
            entries = vlib_all_verses(book_label, chap) or []
            if entries:
                for e in entries:
                    vnum = int(e["verse_number"])
                    vtxt = clean_plain_text(e["verse_text"])
                    theox = format_theological_content(e["explanation"])
                    blocks.append(
                        f"**VERSET {vnum}**\n\n"
                        f"**TEXTE BIBLIQUE :**\n{vtxt}\n\n"
                        f"**EXPLICATION THÉOLOGIQUE :**\n{theox}"
                    )
                return {"content": format_theological_content("\n\n".join(blocks).strip())}
        except Exception as e:
            print(f"VLIB chapter fallback: {e}")

    # Sinon, parser le texte brut et générer verset par verset
    lines = [l for l in text.splitlines() if l.strip()]
    for line in lines:
        m = re.match(r"^(\d+)\.\s*(.*)$", line)
        if not m:
            continue
        vnum = int(m.group(1))
        vtxt = m.group(2).strip()
        theox = await generate_simple_theological_explanation(vtxt, book_label, chap, vnum)
        blocks.append(
            f"**VERSET {vnum}**\n\n"
            f"**TEXTE BIBLIQUE :**\n{vtxt}\n\n"
            f"**EXPLICATION THÉOLOGIQUE :**\n{theox}"
        )
    return {"content": format_theological_content("\n\n".join(blocks).strip())}

# ---- Étude 28 rubriques
@app.post("/api/generate-study")
async def generate_study(request: StudyRequest):
    try:
        passage = request.passage.strip()
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")

        # Forcer chapitre (les 28 points portent sur le chapitre)
        book_label, osis, chap, _ = parse_passage_input(passage)
        bible_id = await get_bible_id()
        text = await fetch_passage_text(bible_id, osis, chap, None)

        rubs = RUBRIQUES_28
        requested_indices = request.requestedRubriques or list(range(len(RUBRIQUES_28)))
        if request.requestedRubriques:
            rubs = [RUBRIQUES_28[i] for i in request.requestedRubriques if 0 <= i < len(RUBRIQUES_28)]
            if not rubs:
                rubs = RUBRIQUES_28
                requested_indices = list(range(len(RUBRIQUES_28)))

        header = f"# Étude Intelligente en 28 points — {book_label} {chap} (Darby)\n"
        intro = (
            "Cette étude utilise une base théologique enrichie (contexte, parallèles, lexique). "
            "Le texte biblique est celui de la **Bible Darby (FR)**."
        )
        excerpt = "\n".join([l for l in text.splitlines()[:8]])
        body: List[str] = [header, "## 📖 Extrait du texte (Darby)\n" + excerpt, intro, "---"]

        # Génération simple et robuste (sans dépendre d'autres modules)
        for i, rubric_idx in enumerate(requested_indices):
            body.append(generate_intelligent_rubric_content(rubric_idx + 1, book_label, chap, text))

        return {"content": "\n\n".join(body).strip()}
    except Exception as e:
        print(f"❌ Erreur generate_study: {e}")
        return {"content": f"Erreur lors de la génération: {str(e)}"}

# ---- Routes dédiées Gemini (optionnelles)
async def generate_enhanced_content_with_gemini(passage: str, rubric_type: str, base_content: str = "") -> str:
    if not (GEMINI_AVAILABLE and EMERGENT_LLM_KEY):
        return base_content or f"Contenu théologique pour {passage} (mode local)"
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"bible_study_{passage.replace(' ', '_')}",
            system_message=(
                "Théologien expert : contenus théologiques riches, contextualisés et fidèles à l'Écriture, en français."
            ),
        ).with_model("gemini", "gemini-2.0-flash")

        if rubric_type == "verse_by_verse":
            prompt = f"""
Génère une étude théologique approfondie verset par verset pour : {passage}

Format par verset :
**TEXTE BIBLIQUE :** [verset]
**EXPLICATION THÉOLOGIQUE :** [analyse 200–300 mots, contexte, doctrine, applications, parallèles]
"""
        elif rubric_type == "thematic_study":
            prompt = f"""
Génère une étude en 28 rubriques complète et substantielle (150–250 mots par rubrique) pour : {passage}
Garde les titres numérotés (1..28) exactement comme attendus.
"""
        else:
            prompt = f"Enrichis théologiquement (200–300 mots) le contenu pour {passage}."

        resp = await chat.send_message(UserMessage(text=prompt))
        return resp or (base_content or f"Contenu théologique pour {passage} (mode local)")
    except Exception as e:
        if any(k in str(e) for k in ("SSL", "TLS", "EOF")):
            return base_content or f"Contenu théologique pour {passage} (mode local)"
        return base_content or f"Contenu théologique pour {passage} (mode fallback)"

@app.post("/api/generate-study-gemini")
async def generate_study_gemini(request: StudyRequest):
    try:
        passage = request.passage.strip()
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")
        enhanced = await generate_enhanced_content_with_gemini(passage, "thematic_study")
        return {"content": enhanced}
    except Exception as e:
        return {"content": "Erreur lors de la génération avec Gemini: " + str(e)}

@app.post("/api/generate-verse-by-verse-gemini")
async def generate_verse_by_verse_gemini(request: StudyRequest):
    try:
        passage = request.passage.strip()
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")
        enhanced = await generate_enhanced_content_with_gemini(passage, "verse_by_verse")
        return {"content": enhanced}
    except Exception as e:
        return {"content": "Erreur lors de la génération avec Gemini: " + str(e)}

# ---- Lancement local
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
