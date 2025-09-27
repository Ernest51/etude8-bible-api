# server.py
# API Bible Study (Darby) — AVEC contenu détaillé verset par verset et explications théologiques automatiques
# - Texte biblique via https://api.scripture.api.bible/v1
# - Étude "28 rubriques" + Verset/verset avec contenu théologique détaillé
# - Génération automatique d'explications théologiques via LLM
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

# Import our new intelligent generators
try:
    from theological_database import theological_db
    INTELLIGENT_MODE = True
    print("✅ Intelligent theological system loaded")
except ImportError:
    INTELLIGENT_MODE = False
    print("⚠️ Fallback to basic mode")

# Import Emergent integrations for Google Gemini Flash
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    GEMINI_AVAILABLE = True
    print("✅ Emergent integrations loaded - Google Gemini Flash available")
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Emergent integrations not available - using fallback mode")

# Charger les variables d'environnement
load_dotenv()

# Configuration Railway
PORT = int(os.getenv("PORT", 8000))

API_BASE = "https://api.scripture.api.bible/v1"
APP_NAME = "Bible Study API - Darby"
BIBLE_API_KEY = os.getenv("BIBLE_API_KEY", "0cff5d83f6852c3044a180cc4cdeb0fe")
PREFERRED_BIBLE_ID = os.getenv("BIBLE_ID", "a93a92589195411f-01")  # Bible J.N. Darby (French)
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY")

# --- CORS ---
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
# GOOGLE GEMINI FLASH INTEGRATION
# =========================
async def generate_enhanced_content_with_gemini(passage: str, rubric_type: str, base_content: str = "") -> str:
    """
    Utilise Google Gemini Flash pour enrichir le contenu théologique
    """
    if not GEMINI_AVAILABLE or not EMERGENT_LLM_KEY:
        print("⚠️ Gemini not available, using base content")
        return base_content
    
    try:
        # Initialiser le chat avec Gemini Flash
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"bible_study_{passage.replace(' ', '_')}",
            system_message=(
                "Tu es un théologien expert spécialisé dans l'étude biblique approfondie. "
                "Tu génères des contenus théologiques riches, contextualisés et spirituellement édifiants en français. "
                "Tes explications sont accessibles mais profondes, toujours fidèles au texte biblique."
            )
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Créer le prompt selon le type de rubrique
        if rubric_type == "verse_by_verse":
            prompt = f"""
Génère une étude théologique approfondie verset par verset pour le passage biblique : {passage}

Pour chaque verset :
1. **TEXTE BIBLIQUE** : Cite le verset exact
2. **EXPLICATION THÉOLOGIQUE** : Analyse approfondie incluant :
   - Contexte historique et culturel
   - Signification théologique
   - Applications spirituelles
   - Références croisées pertinentes

Format souhaité :
**VERSET X**
**TEXTE BIBLIQUE :**
[texte du verset]

**EXPLICATION THÉOLOGIQUE :**
[analyse détaillée du verset]

Assure-toi que chaque explication soit substantielle (200-300 mots) et spirituellement enrichissante.
"""
        elif rubric_type == "thematic_study":
            prompt = f"""
Génère une étude thématique approfondie pour le passage biblique : {passage}

Structure requise avec les 28 rubriques d'étude biblique :

## 1. Prière d'ouverture
[Prière contextuelle pour ce passage]

## 2. Structure littéraire
[Analyse de la structure du passage]

## 3. Questions du chapitre précédent
[Liens avec le contexte précédent]

## 4. Thème doctrinal
[Doctrine principale enseignée]

## 5. Fondements théologiques
[Bases théologiques du passage]

## 6. Contexte historique
[Situation historique]

## 7. Contexte culturel
[Éléments culturels pertinents]

## 8. Contexte géographique
[Aspects géographiques]

## 9. Analyse lexicale
[Mots-clés et leur signification]

## 10. Parallèles bibliques
[Passages similaires dans l'Écriture]

## 11. Prophétie et accomplissement
[Aspects prophétiques le cas échéant]

## 12. Personnages
[Analyse des personnages principaux]

## 13. Structure rhétorique
[Analyse rhétorique du passage]

## 14. Théologie trinitaire
[Aspects trinitaires]

## 15. Christ au centre
[Comment Christ est révélé]

## 16. Évangile et grâce
[Messages de grâce et d'évangile]

## 17. Application personnelle
[Applications pour la vie personnelle]

## 18. Application communautaire
[Applications pour l'église]

## 19. Prière de réponse
[Prière inspirée du passage]

## 20. Questions d'étude
[Questions pour approfondir]

## 21. Points de vigilance
[Éléments à noter particulièrement]

## 22. Objections et réponses
[Réponses aux objections courantes]

## 23. Perspective missionnelle
[Implications missionnaires]

## 24. Éthique chrétienne
[Applications éthiques]

## 25. Louange / liturgie
[Éléments de louange inspirés]

## 26. Méditation guidée
[Guide de méditation]

## 27. Mémoire / versets clés
[Versets à mémoriser]

## 28. Plan d'action
[Actions concrètes à entreprendre]

Chaque section doit être substantielle et adaptée spécifiquement au passage {passage}.
"""
        else:
            prompt = f"Génère un contenu théologique enrichi pour le passage {passage} sur le thème : {rubric_type}. Sois détaillé et spirituellement édifiant."
        
        # Envoyer le message à Gemini
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        print(f"✅ Gemini Flash generated {len(response)} characters for {passage}")
        return response
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erreur Gemini Flash: {e}")
        # Si c'est une erreur SSL/TLS, ne pas l'afficher à l'utilisateur
        if "SSL" in error_msg or "TLS" in error_msg or "EOF" in error_msg or "ssl.c" in error_msg:
            print(f"🔄 SSL/TLS error detected, using fallback mode silently")
            return base_content if base_content else f"Contenu théologique pour {passage} (mode local)"
        return base_content if base_content else f"Contenu théologique pour {passage} (mode fallback)"

# =========================
#      SCHEMAS
# =========================
class StudyRequest(BaseModel):
    passage: str = Field(..., description="Ex: 'Nombres 2' ou 'Jean 3'")
    version: str = Field("", description="Ignoré ici (api.bible gère par bibleId).")
    tokens: int = Field(0, description="Ignoré (hérité du front).")
    model: str = Field("", description="Ignoré (hérité du front).")
    requestedRubriques: Optional[List[int]] = Field(
        None, description="Index des rubriques à produire (0..27). None = toutes."
    )


class VerseByVerseRequest(BaseModel):
    passage: str = Field(..., description="Ex: 'Genèse 1' ou 'Genèse 1:1'")
    version: str = Field("", description="Ignoré (api.bible).")


# =========================
#  OUTILS livres → OSIS
# =========================
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-zA-Z0-9 ]+", " ", s).lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s

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
    "sophonie": "ZEP", "aggée": "HAG", "aggee": "HAG", "zacharie": "ZEC", "malachie": "MAL",
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
        # cherche Darby FR
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


# =========================
#   CONTENU / RUBRIQUES
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

def parse_passage_input(p: str):
    """
    'Genèse 1'    -> ('Genèse', 1, None)
    'Genèse 1:3'  -> ('Genèse', 1, 3)
    'Genèse 1 LSG' / 'Genèse 1:3 LSG' -> idem (version ignorée)
    """
    p = p.strip()
    # tolère un éventuel "version" en fin (un mot ou deux)
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
#   GÉNÉRATION THÉOLOGIQUE SIMPLE (SANS LLM)
# =========================
async def generate_simple_theological_explanation(verse_text: str, book_name: str, chapter: int, verse_num: int) -> str:
    """
    Génère une explication théologique spécifique pour chaque verset en utilisant Gemini Flash
    """
    # Si Gemini est disponible, générer une explication spécifique
    if GEMINI_AVAILABLE and EMERGENT_LLM_KEY:
        try:
            # Créer un prompt spécifique pour ce verset
            prompt = f"""
Génère une explication théologique spécifique et contextuelle pour ce verset biblique :

**Verset** : {book_name} {chapter}:{verse_num}
**Texte** : {verse_text}

INSTRUCTIONS :
- Fournis une explication théologique de 2-3 phrases (150-200 mots maximum)
- Sois spécifique au contenu exact de ce verset (pas générique)
- Inclus le contexte historique ou culturel pertinent
- Évite les répétitions avec d'autres versets
- Utilise un langage accessible mais théologiquement riche
- Réponds UNIQUEMENT avec l'explication, sans introduction

L'explication doit être unique à ce verset précis et à son contexte dans {book_name} chapitre {chapter}.
"""
            
            # Utiliser Gemini pour générer l'explication
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"verse_explanation_{book_name}_{chapter}_{verse_num}",
                system_message="Tu es un théologien expert qui génère des explications bibliques spécifiques et contextuelles en français."
            ).with_model("gemini", "gemini-2.0-flash")
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Nettoyer la réponse
            explanation = response.strip()
            if len(explanation) > 50:  # Vérifier que la réponse est substantielle
                print(f"✅ Gemini generated specific explanation for {book_name} {chapter}:{verse_num}")
                return explanation
                
        except Exception as e:
            print(f"⚠️ Gemini explanation failed for {book_name} {chapter}:{verse_num}: {e}")
            # Si c'est une erreur SSL/TLS, utiliser le fallback immédiatement
            if "SSL" in str(e) or "TLS" in str(e) or "EOF" in str(e):
                print(f"🔄 SSL/TLS error detected, using fallback for {book_name} {chapter}:{verse_num}")
    
    # Fallback vers le système existant si Gemini échoue
    return _generate_fallback_explanation(verse_text, book_name, chapter, verse_num)

def _generate_fallback_explanation(verse_text: str, book_name: str, chapter: int, verse_num: int) -> str:
    """
    Génère une explication théologique basée sur l'analyse intelligente du contenu du verset (mode fallback)
    """
    verse_lower = verse_text.lower()
    explanation_parts = []
    
    # === ANALYSE CONTEXTUELLE PAR LIVRE ET CONTENU SPÉCIFIQUE ===
    
    # Genèse - Contexte de création et origines avec plus de spécificité
    if book_name == "Genèse":
        if chapter == 1:
            if verse_num == 1:
                explanation_parts.append("Ce verset fondamental proclame l'existence éternelle de Dieu et établit le principe de création ex nihilo, révélant Dieu comme la source unique de toute réalité.")
            elif verse_num in [2,3]:
                explanation_parts.append("Cette description révèle le processus créateur divin par la parole, démontrant la puissance absolue de Dieu qui transforme le chaos en ordre par son commandement.")
            elif verse_num == 27:
                explanation_parts.append("Cette création de l'homme à l'image de Dieu révèle la dignité unique de l'humanité et sa vocation à refléter la gloire divine dans la création.")
            elif verse_num >= 28:
                explanation_parts.append("Cette bénédiction divine établit le mandat culturel de l'humanité, révélant sa responsabilité de gérance sur la création sous l'autorité divine.")
        elif chapter == 2:
            explanation_parts.append("Ce récit complémentaire révèle la dimension relationnelle de la création et l'intimité originelle entre Dieu et l'humanité dans le jardin d'Éden.")
        elif chapter == 3:
            explanation_parts.append("Cette narration de la chute révèle l'origine du mal et l'inauguration du plan de rédemption à travers la promesse messianique.")
        elif chapter == 6:
            if "fils de Dieu" in verse_lower or "filles des hommes" in verse_lower:
                explanation_parts.append("Ce passage controversé révèle la corruption progressive de l'humanité et l'effacement de la distinction entre la lignée pieuse et impie, préparant le jugement du déluge.")
            elif "mon esprit" in verse_lower or "120 ans" in verse_lower:
                explanation_parts.append("Cette limitation divine révèle à la fois la patience de Dieu et sa justice, accordant un temps de grâce avant le jugement tout en maintenant ses standards moraux.")
            elif "géants" in verse_lower or "nephilim" in verse_lower:
                explanation_parts.append("Cette mention des géants illustre l'ampleur de la corruption qui caractérise l'humanité prédiluvienne, justifiant l'intervention divine radicale du déluge.")
            elif "méchanceté" in verse_lower or "mal" in verse_lower:
                explanation_parts.append("Cette évaluation divine révèle l'état de corruption totale du cœur humain, démontrant la nécessité de l'intervention divine pour la rédemption.")
            elif "repentit" in verse_lower or "affligea" in verse_lower:
                explanation_parts.append("Cette expression anthropomorphique révèle la douleur divine face au péché, illustrant l'amour de Dieu pour sa création tout en maintenant sa justice.")
            elif "noé" in verse_lower and "grâce" in verse_lower:
                explanation_parts.append("Cette découverte de grâce révèle le principe de l'élection divine et de la préservation d'un reste fidèle, préfigurant le salut par grâce.")
            elif "juste" in verse_lower or "parfait" in verse_lower or "marchait avec dieu" in verse_lower:
                explanation_parts.append("Cette caractérisation de Noé révèle les qualités requises pour trouver grâce devant Dieu : la justice, l'intégrité et la communion spirituelle.")
            elif "corruption" in verse_lower or "violence" in verse_lower:
                explanation_parts.append("Cette description de l'état moral du monde révèle les conséquences de l'éloignement de Dieu : la corruption spirituelle et la violence sociale.")
            elif "fin de toute chair" in verse_lower or "détruire" in verse_lower:
                explanation_parts.append("Cette annonce du jugement révèle la justice inexorable de Dieu face au péché, tout en préparant la voie pour un nouveau commencement à travers Noé.")
            elif "arche" in verse_lower or "bois de gopher" in verse_lower:
                explanation_parts.append("Ces instructions détaillées révèlent la provision divine de salut au cœur même du jugement, préfigurant l'œuvre rédemptrice du Christ.")
            else:
                explanation_parts.append(f"Ce verset du chapitre 6 de la Genèse révèle un aspect important de la condition humaine avant le déluge et de la réponse divine à la corruption.")
        else:
            explanation_parts.append(f"Ce passage de Genèse {chapter} révèle les développements du plan divin dans l'histoire des origines.")
    
    # Continuer avec les autres livres mais de manière plus spécifique...
    elif book_name == "Jean":
        if chapter == 3:
            if verse_num == 16:
                explanation_parts.append("Ce verset central de l'Évangile révèle la motivation divine du salut : l'amour, et sa manifestation suprême : le don du Fils unique pour la vie éternelle.")
            elif verse_num == 3:
                explanation_parts.append("Cette exigence de nouvelle naissance révèle la nécessité de la régénération spirituelle pour entrer dans le royaume de Dieu.")
            else:
                explanation_parts.append(f"Ce verset du dialogue avec Nicodème révèle les conditions et la nature de la vie spirituelle authentique.")
        else:
            explanation_parts.append(f"Ce passage de Jean {chapter} révèle la divinité du Christ et les implications pour la foi.")
    
    # Si aucune analyse spécifique n'est trouvée, utiliser le contexte général du livre
    if not explanation_parts:
        book_contexts = {
            "Genèse": f"Ce verset du chapitre {chapter} révèle un aspect des origines et du plan divin pour l'humanité.",
            "Exode": f"Ce passage du chapitre {chapter} illustre l'œuvre libératrice de Dieu et ses implications spirituelles.",
            "Jean": f"Ce verset du chapitre {chapter} révèle la personne et l'œuvre du Christ pour le salut.",
            "Romains": f"Cette doctrine du chapitre {chapter} expose les fondements du salut par la foi en Christ."
        }
        explanation_parts.append(book_contexts.get(book_name, f"Ce verset révèle un aspect important de la révélation divine dans {book_name} {chapter}."))
    
    # Joindre les explications
    full_explanation = " ".join(explanation_parts)
    
    # Nettoyer le texte
    full_explanation = full_explanation.replace("strong", "").replace("Strong", "")
    full_explanation = ' '.join(full_explanation.split())
    
    return full_explanation

def format_theological_content(content: str) -> str:
    """
    Formate le contenu théologique de manière simple et lisible SANS étoiles
    """
    import re
    
    # SUPPRIMER TOUTES LES ÉTOILES pour éviter l'affichage des **
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # **texte** → texte
    content = content.replace('**', '')  # Supprimer toutes les étoiles restantes
    content = content.replace('*', '')   # Supprimer les étoiles simples aussi
    
    # Supprimer le mot "strong" isolé
    content = re.sub(r'\bstrong\b', '', content, flags=re.IGNORECASE)
    
    # Nettoyer les espaces multiples mais GARDER les retours à la ligne
    content = re.sub(r'[ ]+', ' ', content)  # Espaces multiples seulement
    content = content.strip()
    
    return content


def generate_intelligent_rubric_content(rubric_num: int, book_name: str, chapter: int, text: str, historical_context: str = "", cross_refs = None) -> str:
    """
    Génère un contenu intelligent pour une rubrique spécifique basé sur le contexte théologique
    """
    if cross_refs is None:
        cross_refs = []
    
    rubric_name = RUBRIQUES_28[rubric_num - 1] if rubric_num <= len(RUBRIQUES_28) else f"Rubrique {rubric_num}"
    
    # Contenu de base contextualisé par rubrique
    base_content = {
        1: f"Seigneur, ouvre nos cœurs à la compréhension de {book_name} {chapter}. Que ton Esprit nous guide dans cette étude.",
        2: f"Le chapitre {chapter} de {book_name} présente une structure littéraire révélant la progression divine du récit.",
        3: f"Les questions soulevées dans le chapitre précédent trouvent leur développement dans {book_name} {chapter}.",
        4: f"Le thème doctrinal central de {book_name} {chapter} révèle des vérités fondamentales sur la nature de Dieu.",
        5: f"Les fondements théologiques de ce passage s'enracinent dans la révélation progressive de Dieu.",
        6: f"Le contexte historique de {book_name} {chapter} éclaire la situation du peuple de Dieu à cette époque.",
        7: f"Les éléments culturels de ce passage révèlent les coutumes et pratiques de l'époque biblique.",
        8: f"La géographie de {book_name} {chapter} situe les événements dans leur cadre territorial significatif.",
        9: f"L'analyse lexicale révèle la richesse des termes hébreux/grecs utilisés dans ce passage.",
        10: f"Les parallèles bibliques enrichissent notre compréhension de {book_name} {chapter}.",
        11: f"Les éléments prophétiques de ce passage trouvent leur accomplissement dans l'histoire du salut.",
        12: f"Les personnages de {book_name} {chapter} illustrent différents aspects de la foi et de l'obéissance.",
        13: f"La structure rhétorique révèle l'art littéraire inspiré de l'auteur biblique.",
        14: f"La théologie trinitaire transparaît dans l'œuvre du Père, du Fils et du Saint-Esprit.",
        15: f"Christ se révèle au centre de {book_name} {chapter} comme accomplissement des promesses divines.",
        16: f"L'évangile et la grâce de Dieu brillent à travers les vérités de ce passage.",
        17: f"Application personnelle: Comment {book_name} {chapter} transforme-t-il notre marche avec Dieu?",
        18: f"Application communautaire: Quelles implications pour l'Église dans {book_name} {chapter}?",
        19: f"Seigneur, que les vérités de {book_name} {chapter} transforment nos cœurs et nos vies.",
        20: f"Questions d'étude pour approfondir la compréhension de {book_name} {chapter}.",
        21: f"Points de vigilance: Quelles erreurs d'interprétation éviter dans ce passage?",
        22: f"Objections courantes et réponses bibliques concernant {book_name} {chapter}.",
        23: f"Perspective missionnelle: Comment ce passage inspire-t-il l'évangélisation?",
        24: f"Éthique chrétienne: Quels principes moraux ressortent de {book_name} {chapter}?",
        25: f"Louange et liturgie inspirées par les vérités de {book_name} {chapter}.",
        26: f"Méditation guidée sur les richesses spirituelles de ce passage.",
        27: f"Versets clés à mémoriser dans {book_name} {chapter}.",
        28: f"Plan d'action concret basé sur les enseignements de {book_name} {chapter}."
    }
    
    content = base_content.get(rubric_num, f"Contenu intelligent pour la rubrique {rubric_num} de {book_name} {chapter}")
    
    # Ajouter le contexte historique si disponible
    if historical_context:
        content += f"\n\nContexte historique: {historical_context}"
    
    # Ajouter les références croisées si disponibles
    if cross_refs:
        # Convertir les objets CrossReference en chaînes de caractères
        ref_strings = []
        for ref in cross_refs[:3]:  # Limiter à 3 références
            if hasattr(ref, 'book') and hasattr(ref, 'chapter'):
                if hasattr(ref, 'verse') and ref.verse:
                    ref_strings.append(f"{ref.book} {ref.chapter}:{ref.verse}")
                else:
                    ref_strings.append(f"{ref.book} {ref.chapter}")
            else:
                # Si c'est déjà une chaîne de caractères
                ref_strings.append(str(ref))
        
        if ref_strings:
            content += f"\n\nRéférences croisées: {', '.join(ref_strings)}"
    
    return f"## {rubric_num}. {rubric_name}\n\n{content}"


# =========================
#        ROUTES
# =========================
@app.get("/api/")
async def root():
    return {"message": "Bible Study API - Railway", "status": "online", "version": "2.0.0", "gemini_available": GEMINI_AVAILABLE}

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok", 
        "bibleId": PREFERRED_BIBLE_ID,
        "gemini_enabled": GEMINI_AVAILABLE,
        "intelligent_mode": INTELLIGENT_MODE
    }

# =========================
#   ROUTES PROXY pour contourner CORS
# =========================
@app.get("/api/test")
async def test_connection():
    """Route de test simple pour vérifier la connexion"""
    return {"status": "Backend accessible", "message": "Connexion OK"}

@app.post("/api/proxy-verse-by-verse")
async def proxy_verse_by_verse(req: VerseByVerseRequest):
    """Proxy vers l'API externe etude8-bible-api-production.up.railway.app"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://etude8-bible-api-production.up.railway.app/api/generate-verse-by-verse",
                headers={"Content-Type": "application/json"},
                json={"passage": req.passage, "version": req.version}
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur proxy verse-by-verse: {str(e)}")


@app.post("/api/generate-verse-by-verse")
async def generate_verse_by_verse(request: StudyRequest):
    """
    Génère une étude verset par verset avec option Gemini Flash
    """
    try:
        passage = request.passage.strip()
        use_gemini = getattr(request, 'use_gemini', False)  # Nouveau paramètre optionnel
        
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")
        
        # Générer le contenu de base
        base_content = await _generate_verse_by_verse_content(request)
        
        # Si Gemini est demandé, enrichir le contenu
        if use_gemini and GEMINI_AVAILABLE:
            print(f"🚀 Enhancing verse-by-verse with Gemini Flash for {passage}")
            enhanced_content = await generate_enhanced_content_with_gemini(
                passage=passage,
                rubric_type="verse_by_verse",
                base_content=base_content.get("content", "")
            )
            return {"content": enhanced_content}
        else:
            return base_content
            
    except Exception as e:
        print(f"❌ Erreur generate_verse_by_verse: {e}")
        return {"content": f"Erreur lors de la génération: {str(e)}"}

async def _generate_verse_by_verse_content(req):
    """Génère le contenu verset par verset de base"""
    book_label, osis, chap, verse = parse_passage_input(req.passage)
    bible_id = await get_bible_id()
    text = await fetch_passage_text(bible_id, osis, chap, verse)

    title = f"**Étude Verset par Verset - {book_label} Chapitre {chap}**"
    intro = (
        "Introduction au Chapitre\n\n"
        "Cette étude parcourt le texte de la **Bible Darby (FR)**. "
        "Les sections *EXPLICATION THÉOLOGIQUE* sont générées automatiquement par IA théologique."
    )

    if verse:
        # Générer l'explication théologique pour le verset unique
        theological_explanation = await generate_simple_theological_explanation(text, book_label, chap, verse)
        theological_explanation = format_theological_content(theological_explanation)
        content = (
            f"**{title}**\n\n{intro}\n\n"
            f"**VERSET {verse}**\n\n"
            f"**TEXTE BIBLIQUE :**\n{text}\n\n"
            f"**EXPLICATION THÉOLOGIQUE :**\n{theological_explanation}"
        )
        return {"content": format_theological_content(content)}

    # Pour un chapitre entier, parser les versets et générer les explications
    lines = [l for l in text.splitlines() if l.strip()]
    blocks: List[str] = [f"**{title}**\n\n{intro}"]
    
    for line in lines:
        m = re.match(r"^(\d+)\.\s*(.*)$", line)
        if not m:
            continue
        vnum = int(m.group(1))
        vtxt = m.group(2).strip()
        
        # Générer l'explication théologique pour CHAQUE verset
        theological_explanation = await generate_simple_theological_explanation(vtxt, book_label, chap, vnum)
        
        blocks.append(
            f"**VERSET {vnum}**\n\n"
            f"**TEXTE BIBLIQUE :**\n{vtxt}\n\n"
            f"**EXPLICATION THÉOLOGIQUE :**\n{theological_explanation}"
        )
    return {"content": format_theological_content("\n\n".join(blocks).strip())}

def generate_intelligent_rubric_content(rubric_index: int, book: str, chapter: int, 
                                       verse_text: str, historical_context: str, cross_refs: list) -> str:
    """Génère le contenu intelligent pour une rubrique spécifique"""
    
    # Utiliser notre générateur intelligent si disponible
    if INTELLIGENT_MODE:
        try:
            from theological_database import theological_db
            
            # Générateur intelligent pour quelques rubriques clés
            if rubric_index == 1:  # Prière d'ouverture
                if book == "Genèse" and chapter == 1:
                    return """## 1. Prière d'ouverture

**ADORATION :**
Père céleste, nous Te reconnaissons comme le Créateur souverain de toutes choses. Comme le déclare Ta Parole : "Au commencement, Dieu créa les cieux et la terre" (Genèse 1:1). Tu es l'Alpha et l'Oméga, Celui qui donne la vie et qui soutient toute création par Ta puissance.

**CONFESSION :**
Nous confessons notre orgueil qui nous fait parfois oublier que nous sommes Tes créatures, entièrement dépendantes de Ta grâce. Pardonne-nous de ne pas toujours reconnaître Ta souveraineté sur nos vies et sur l'univers entier.

**DEMANDE :**
Accorde-nous la sagesse spirituelle pour comprendre les mystères de Ta création révélés dans ce premier chapitre. Que Ton Esprit illumine notre intelligence pour saisir la beauté de Ton œuvre créatrice et son message pour nos cœurs aujourd'hui."""
                
                elif book == "Jean" and chapter == 1:  
                    return """## 1. Prière d'ouverture

**ADORATION :**
Seigneur Jésus, Logos éternel, nous T'adorons comme la Parole qui était au commencement avec Dieu et qui était Dieu (Jean 1:1). Tu es la lumière véritable qui éclaire tout homme en venant dans le monde.

**CONFESSION :**
Nous confessons que trop souvent nous n'avons pas reçu Ta lumière, préférant nos ténèbres spirituelles à Ta vérité. Pardonne notre résistance à Ta révélation parfaite.

**DEMANDE :**
Ouvre nos cœurs pour recevoir la révélation suprême de Dieu en Christ. Que nous comprenions la profondeur du mystère de l'Incarnation révélé dans ce prologue majestueux."""
                
                else:
                    return f"""## 1. Prière d'ouverture

**ADORATION :**
Père éternel, nous Te reconnaissons comme le Dieu qui Se révèle progressivement à travers Sa Parole. Dans {book} {chapter}, Tu continues de déployer Ton plan parfait pour l'humanité.

**CONFESSION :**
Nous nous plaçons humblement dans Ta lumière, confessant nos faiblesses et notre besoin constant de Ta grâce. Purifie nos cœurs pour recevoir Ta vérité.

**DEMANDE :**
Accorde-nous la sagesse et la compréhension spirituelle pour saisir les enseignements de ce chapitre. Que Ton Esprit nous guide dans toute la vérité."""
            
            elif rubric_index == 6:  # Contexte historique
                historical_ctx = theological_db.get_historical_context(book, chapter)
                return f"""## 6. Contexte historique

{historical_ctx}

**CHRONOLOGIE BIBLIQUE :**
Ce passage de {book} {chapter} s'inscrit dans l'histoire de la révélation progressive de Dieu à l'humanité.

**IMPLICATIONS HISTORIQUES :**
La compréhension du contexte historique éclaire les enjeux spirituels et pratiques que ce texte adressait aux premiers destinataires."""
            
            elif rubric_index == 10:  # Parallèles bibliques
                cross_refs_db = theological_db.get_cross_references(book, chapter)
                if cross_refs_db:
                    refs_text = "\n".join([f"**{ref.book} {ref.chapter}:{ref.verse or ''}** - {ref.context}" 
                                         for ref in cross_refs_db[:4]])
                    return f"""## 10. Parallèles bibliques 

**RÉFÉRENCES CROISÉES PRINCIPALES :**

{refs_text}

**PRINCIPE DE L'ANALOGIE DE LA FOI :**
L'Écriture s'interprète par l'Écriture. Ces passages parallèles éclairent et confirment les vérités révélées ici."""
                else:
                    return f"""## 10. Parallèles bibliques

Ce passage de {book} {chapter} trouve des échos dans toute l'Écriture, révélant l'unité organique de la révélation divine."""
            
            else:
                # Rubrique générique intelligente
                rubric_names = [
                    "", "Prière d'ouverture", "Structure littéraire", "Questions du chapitre précédent",
                    "Thème doctrinal", "Fondements théologiques", "Contexte historique", "Contexte culturel",
                    "Contexte géographique", "Analyse lexicale", "Parallèles bibliques", "Prophétie et accomplissement",
                    "Personnages", "Structure rhétorique", "Théologie trinitaire", "Christ au centre",
                    "Évangile et grâce", "Application personnelle", "Application communautaire", "Prière de réponse",
                    "Questions d'étude", "Points de vigilance", "Objections et réponses", "Perspective missionnelle",
                    "Éthique chrétienne", "Louange / liturgie", "Méditation guidée", "Mémoire / versets clés", "Plan d'action"
                ]
                
                rubric_name = rubric_names[rubric_index] if rubric_index < len(rubric_names) else f"Rubrique {rubric_index}"
                
                return f"""## {rubric_index}. {rubric_name}

**ANALYSE CONTEXTUELLE DE {book.upper()} {chapter} :**
Ce passage révèle des vérités spécifiques sur la nature de Dieu et Son œuvre dans l'histoire du salut.

**ENSEIGNEMENT CENTRAL :**
L'étude de ce texte dans son contexte historique et théologique révèle des principes durables pour la vie chrétienne.

**APPLICATION PRATIQUE :**
Comment ces vérités transforment-elles notre compréhension de Dieu et notre réponse de foi ?"""
                
        except Exception as e:
            print(f"Erreur génération rubrique {rubric_index}: {e}")
    
    # Fallback
    return f"""## {rubric_index}. Rubrique {rubric_index}

**Contenu contextualisé pour {book} {chapter}**

Cette rubrique révèle des aspects importants de la vérité divine spécifiques à ce passage."""


@app.post("/api/generate-study")
async def generate_study(request: StudyRequest):
    """
    Génère une étude biblique avec système intelligent + option Gemini Flash
    """
    try:
        passage = request.passage.strip()
        use_gemini = getattr(request, 'use_gemini', False)  # Nouveau paramètre optionnel
        
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")
        
        # Générer le contenu de base avec le système intelligent existant
        base_response = await _generate_intelligent_study(request)
        
        # Si Gemini est demandé, enrichir le contenu
        if use_gemini and GEMINI_AVAILABLE:
            print(f"🚀 Enhancing with Gemini Flash for {passage}")
            enhanced_content = await generate_enhanced_content_with_gemini(
                passage=passage,
                rubric_type="thematic_study",
                base_content=base_response.get("content", "")
            )
            return {"content": enhanced_content}
        else:
            return base_response
            
    except Exception as e:
        print(f"❌ Erreur generate_study: {e}")
        return {"content": f"Erreur lors de la génération: {str(e)}"}

async def _generate_intelligent_study(req: StudyRequest):
    """
    Étude '28 rubriques' INTELLIGENTE avec contenu contextualisé.
    - Récupère le texte (Darby) pour *le chapitre* demandé.
    - Génère un contenu intelligent pour chaque rubrique basé sur le contexte.
    """
    book_label, osis, chap, verse = parse_passage_input(req.passage)
    # On force "passage = chapitre" pour la 28 pts
    verse = None

    bible_id = await get_bible_id()
    text = await fetch_passage_text(bible_id, osis, chap, verse)

    # Filtre des rubriques
    rubs = RUBRIQUES_28
    requested_indices = req.requestedRubriques or list(range(len(RUBRIQUES_28)))
    
    if req.requestedRubriques:
        rubs = [RUBRIQUES_28[i] for i in req.requestedRubriques if 0 <= i < len(RUBRIQUES_28)]
        if not rubs:
            rubs = RUBRIQUES_28
            requested_indices = list(range(len(RUBRIQUES_28)))

    header = f"# Étude Intelligente en 28 points — {book_label} {chap} (Darby)\n"
    intro = (
        "Cette étude utilise une **base théologique enrichie** avec références croisées, "
        "contextes historiques et culturels, et analyses lexicales automatiques. "
        "Le texte biblique est celui de la **Bible Darby (FR)**."
    )
    
    # Petit extrait du chapitre (lisible dans le front)
    excerpt = "\n".join([l for l in text.splitlines()[:8]])
    body: List[str] = [
        header, 
        "## 📖 Extrait du texte (Darby)\n" + excerpt, 
        intro, 
        "---"
    ]

    # GÉNÉRATION INTELLIGENTE pour chaque rubrique
    if INTELLIGENT_MODE:
        try:
            for i, rubric_idx in enumerate(requested_indices):
                if rubric_idx < len(RUBRIQUES_28):
                    # Utiliser le générateur intelligent
                    from theological_database import theological_db
                    
                    # Contexte intelligent basé sur le livre
                    cross_refs = theological_db.get_cross_references(book_label, chap)
                    historical_context = theological_db.get_historical_context(book_label, chap)
                    
                    # Génération spécialisée par rubrique
                    rubric_content = generate_intelligent_rubric_content(
                        rubric_idx + 1, book_label, chap, text, historical_context, cross_refs
                    )
                    body.append(rubric_content)
        except Exception as e:
            print(f"Erreur génération intelligente: {e}")
            # Fallback vers le mode basique
            for i, r in enumerate(rubs, start=1):
                body.append(f"## {i}. {r}\n\n**Contenu contextualisé à développer pour {book_label} {chap}**\n\nCette rubrique révèle des aspects importants de la vérité divine spécifiques à ce passage.")
    else:
        # Mode basique amélioré
        for i, r in enumerate(rubs, start=1):
            body.append(f"## {i}. {r}\n\n**Contenu contextualisé pour {book_label} {chap}**\n\nCette rubrique révèle des aspects importants de la vérité divine spécifiques à ce passage.")

    return {"content": "\n\n".join(body).strip()}

# --- ROUTES PROXY POUR RAILWAY APIS ---
@app.post("/api/verse-proxy")
async def verse_proxy_to_railway(req: StudyRequest):
    """Proxy vers etude8-bible-api Railway pour éviter CORS"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://etude8-bible-api-production.up.railway.app/api/generate-verse-by-verse",
                json=req.dict(),
                headers={"Content-Type": "application/json"}
            )
            return response.json()
    except Exception as e:
        print(f"❌ Proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

@app.post("/api/study-proxy") 
async def study_proxy_to_railway(req: StudyRequest):
    """Proxy vers etude28-bible-api Railway pour éviter CORS"""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://etude28-bible-api-production.up.railway.app/api/generate-study",
                json=req.dict(),
                headers={"Content-Type": "application/json"}
            )
            return response.json()
    except Exception as e:
        print(f"❌ Proxy error: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

# --- ROUTES PROXY POUR COMPATIBILITÉ ---
@app.post("/api/proxy-28-study")
async def proxy_28_study(req: StudyRequest):
    """Proxy vers notre générateur intelligent local - utilise generate_28"""
    return await generate_28(req)

@app.post("/api/proxy-verse-by-verse") 
async def proxy_verse_by_verse(req: StudyRequest):
    """Proxy vers notre générateur intelligent local"""
    return await generate_verse_by_verse(req)

@app.post("/api/generate-28")
async def generate_28(req: StudyRequest):
    """Alias pour compatibilité"""
    return await generate_study(req)


# Lancement local
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)

# Routes dédiées Gemini Flash
@app.post("/api/generate-study-gemini")
async def generate_study_gemini(request: StudyRequest):
    """Génère une étude biblique exclusivement avec Gemini Flash"""
    try:
        passage = request.passage.strip()
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")
            
        print("🚀 Generating with Gemini Flash for " + passage)
        enhanced_content = await generate_enhanced_content_with_gemini(
            passage=passage,
            rubric_type="thematic_study"
        )
        return {"content": enhanced_content}
        
    except Exception as e:
        print("❌ Erreur generate_study_gemini: " + str(e))
        return {"content": "Erreur lors de la génération avec Gemini: " + str(e)}

@app.post("/api/generate-verse-by-verse-gemini")
async def generate_verse_by_verse_gemini(request: StudyRequest):
    """Génère une étude verset par verset exclusivement avec Gemini Flash"""
    try:
        passage = request.passage.strip()
        if not passage:
            raise HTTPException(status_code=400, detail="Passage requis")
            
        print("🚀 Generating verse-by-verse with Gemini Flash for " + passage)
        enhanced_content = await generate_enhanced_content_with_gemini(
            passage=passage,
            rubric_type="verse_by_verse"
        )
        return {"content": enhanced_content}
        
    except Exception as e:
        print("❌ Erreur generate_verse_by_verse_gemini: " + str(e))
        return {"content": "Erreur lors de la génération avec Gemini: " + str(e)}
