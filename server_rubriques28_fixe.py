import os, re, random, hashlib
from typing import List, Dict, Any, Optional, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_NAME = "Bible Study - 28 Rubriques"
FRONTEND_ALLOWED = os.getenv("FRONTEND_ORIGIN", "https://etude8-bible.vercel.app")

app = FastAPI(title=APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ALLOWED, 
        "https://etude-bible-app.preview.emergentagent.com",  # ← AJOUTÉ POUR EMERGENT
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Entrée / schémas
# -----------------------------

class GenerateStudyRequest(BaseModel):
    passage: str = Field(..., description="Ex: 'Genèse 1' ou 'Jean 3'")
    version: str = Field("LSG", description="Affichage indicatif")
    tokens: int = Field(500, description="Taille indicative")
    model: str = Field("local", description="Nom du modèle (placeholder)")
    requestedRubriques: List[int] = Field(default_factory=list, description="Indices de rubriques souhaitées (0..27)")

# -----------------------------
# Rubriques (28 titres fixes)
# -----------------------------

RUBRIQUES_28 = [
    "Étude verset par verset", "Prière d'ouverture", "Structure littéraire",
    "Questions du chapitre précédent", "Thème doctrinal", "Fondements théologiques",
    "Contexte historique", "Contexte culturel", "Contexte géographique",
    "Analyse lexicale", "Parallèles bibliques", "Prophétie et accomplissement",
    "Personnages", "Structure rhétorique", "Théologie trinitaire", "Christ au centre",
    "Évangile et grâce", "Application personnelle", "Application communautaire",
    "Prière de réponse", "Questions d'étude", "Points de vigilance",
    "Objections et réponses", "Perspective missionnelle", "Éthique chrétienne",
    "Louange / liturgie", "Méditation guidée", "Mémoire / versets clés", "Plan d'action"
]

# -----------------------------
# Profils simples par livres (pour teinter le contenu)
# -----------------------------

BOOK_CLUSTERS: Dict[str, str] = {
    # Pentateuque
    "Genèse":"origines", "Exode":"liberation", "Lévitique":"sacerdotal", "Nombres":"pelerinage", "Deutéronome":"alliance",
    # Poétiques
    "Job":"sagesse", "Psaumes":"louange", "Proverbes":"sagesse", "Ecclésiaste":"sagesse", "Cantique":"poesie",
    # Prophètes (échantillon)
    "Ésaïe":"prophetie", "Jérémie":"prophetie", "Ézéchiel":"prophetie", "Daniel":"prophetie",
    # Évangiles & Actes
    "Matthieu":"evangile", "Marc":"evangile", "Luc":"evangile", "Jean":"evangile", "Actes":"eglise",
    # Épîtres (échantillon)
    "Romains":"doctrine", "1 Corinthiens":"eglise", "2 Corinthiens":"eglise",
    "Galates":"doctrine", "Éphésiens":"eglise", "Philippiens":"eglise",
    "Colossiens":"doctrine", "1 Thessaloniciens":"eglise", "2 Thessaloniciens":"eglise",
    "1 Timothée":"pastoral", "2 Timothée":"pastoral", "Tite":"pastoral", "Philémon":"pastoral",
    "Hébreux":"christologie", "Jacques":"ethique", "1 Pierre":"ethique", "2 Pierre":"ethique",
    "1 Jean":"ethique", "2 Jean":"ethique", "3 Jean":"ethique", "Jude":"ethique",
    "Apocalypse":"apocalypse"
}

CLUSTER_HINTS: Dict[str, List[str]] = {
    "origines": ["création", "image de Dieu", "promesse", "alliance", "patriarches"],
    "liberation": ["Pâque", "Exode", "alliance sinaïtique", "loi", "tabernacle"],
    "sacerdotal": ["sacrifice", "sainteté", "sacerdoce", "pureté", "culte"],
    "pelerinage": ["désert", "murmures", "guidance divine", "organisation tribale"],
    "alliance": ["rappel de la Loi", "bénédictions et malédictions", "fidélité"],
    "sagesse": ["crainte de l'Éternel", "vanité des vanités", "l'épreuve", "sagesse pratique"],
    "poesie": ["amour", "métaphores", "dialogue", "poésie hébraïque"],
    "prophetie": ["appel à la repentance", "jugement et restauration", "Messie", "Nouveau Testament en germe"],
    "evangile": ["royaume de Dieu", "discipulat", "paraboles", "signes"],
    "eglise": ["Pentecôte", "mission", "édification", "dons", "unité"],
    "doctrine": ["justification", "grâce", "Christ suffisant", "vie nouvelle"],
    "pastoral": ["établir des anciens", "enseignement sain", "piété", "réfuter l'erreur"],
    "christologie": ["supériorité du Christ", "sacerdoce selon Melchisédek", "nouvelle alliance"],
    "ethique": ["foi vivante", "espérance au milieu de l'épreuve", "amour fraternel"],
    "apocalypse": ["persévérance", "victoire de l'Agneau", "symboles", "nouvelle création"]
}

# -----------------------------
# Utilitaires
# -----------------------------

BOOK_REGEX = r"^\s*([1-3]?\s?[A-Za-zÉÈÊËÀÂÎÏÔÙÛÜÇéèêëàâîïôùûüç\-'' ]+)\s+(\d+)(?::\d+)?(?:\s+\S.*)?$"

def parse_passage(p: str) -> Tuple[str, int]:
    m = re.match(BOOK_REGEX, p.strip())
    if not m:
        raise HTTPException(status_code=400, detail="Format attendu: 'Livre Chapitre' ou 'Livre Chapitre:Verset'")
    book = m.group(1).strip()
    chapter = int(m.group(2))
    return book, chapter

def seed_for(book: str, chapter: int) -> int:
    key = f"{book}|{chapter}".encode("utf-8")
    return int(hashlib.sha256(key).hexdigest(), 16) % (2**31)

def cluster_for(book: str) -> str:
    return BOOK_CLUSTERS.get(book, "general")

def generate_section(title: str, book: str, chapter: int, cluster: str, rnd: random.Random) -> List[str]:
    """Génère des bullets pour une section donnée."""
    
    hints = CLUSTER_HINTS.get(cluster, ["contexte", "application", "réflexion"])
    
    if "verset par verset" in title.lower():
        base = [
            f"- Repérage des divisions du texte ({book} {chapter}).",
            "- Points saillants par péricopes.",
            "- Transitions et refrains.",
        ]
    elif "prière" in title.lower() and "ouverture" in title.lower():
        base = [
            "- Adoration : reconnaître Dieu pour qui Il est.",
            "- Confession : se placer dans la lumière.",
            "- Demande : sagesse et compréhension du passage.",
        ]
    elif "questions d'étude" in title.lower():
        base = [
            "- Que révèle ce chapitre sur Dieu ?",
            "- Que révèle ce chapitre sur l'homme ?",
            "- Qu'appelle-t-il à changer aujourd'hui ?",
        ]
    elif "mémoire / versets clés" in title.lower():
        base = [
            f"- Verset-clé suggéré : {book} {chapter}:{rnd.randint(1, max(3, chapter%30+1))}",
            "- Mémo : écris-le et médite-le cette semaine.",
        ]
    elif "plan d'action" in title.lower():
        base = [
            "- Une action personnelle cette semaine.",
            "- Une action communautaire ce mois-ci.",
            "- Un témoignage à partager.",
        ]
    else:
        # Contenu générique contextuel
        hint = rnd.choice(hints)
        base = [
            f"- Contexte ({book} {chapter}) : {hint}.",
            f"- Lien biblique : {rnd.choice(['signes', 'paraboles', 'royaume de Dieu', 'discipulat'])}.",
            "- Application : une mise en pratique concrète.",
        ]
    
    return base

def make_content(book: str, chapter: int, version: str, rubriques: List[int] | None) -> str:
    cl = cluster_for(book)
    rnd = random.Random(seed_for(book, chapter))
    indices = rubriques if rubriques else list(range(len(RUBRIQUES_28)))
    
    lines: List[str] = []
    lines.append("**ÉTUDE BIBLIQUE — 28 RUBRIQUES**")
    lines.append(f"**Passage :** {book} {chapter} ({version})\n")
    
    for i in indices:
        title = RUBRIQUES_28[i]
        lines.append(f"## {i}. {title}")
        for bullet in generate_section(title, book, chapter, cl, rnd):
            lines.append(bullet)
        lines.append("")  # ligne vide
    
    return "\n".join(lines).strip()

# -----------------------------
# Routes
# -----------------------------

@app.get("/")
def root():
    return {"message": APP_NAME, "status": "online"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "service": "28-rubriques"}

@app.post("/api/generate-study")
def generate_study(body: GenerateStudyRequest) -> Dict[str, Any]:
    try:
        book, chap = parse_passage(body.passage)
        content = make_content(book, chap, body.version, body.requestedRubriques or None)
        return {"content": content}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération 28 rubriques : {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)