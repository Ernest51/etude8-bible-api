/* eslint-disable */
import React, { useState, useEffect, useMemo } from "react";
import "./App.css";
import "./rubriques.css";
import RubriquesInline from "./RubriquesInline";

/* =========================
   Configuration et Helpers
========================= */

// Backend: 1) REACT_APP_BACKEND_URL si défini (nettoyé), 2) localhost en dev, 3) Railway en prod
const getBackendUrl = () => {
  const raw = (process.env.REACT_APP_BACKEND_URL || "").trim();
  // retire guillemets accidentels & slash final
  const cleaned = raw.replace(/^["']|["']$/g, "").replace(/\/+$/g, "");
  if (cleaned) return cleaned;

  const hostname = typeof window !== "undefined" ? window.location.hostname : "";
  if (hostname === "localhost" || hostname === "127.0.0.1") return "http://localhost:8001";
  // (optionnel) si tu utilises encore preview.emergentagent.com
  if (hostname.includes("preview.emergentagent.com")) return `https://${hostname}`;
  // fallback prod → Railway
  return "https://etude8-bible-api-production.up.railway.app";
};

const BACKEND_URL = getBackendUrl();
const API_BASE = `${BACKEND_URL.replace(/\/+$/g, "")}/api`;

if (typeof window !== "undefined") {
  console.log("[App] BACKEND_URL =", BACKEND_URL);
  console.log("[App] API_BASE     =", API_BASE);
}

function asString(x) {
  if (x === undefined || x === null) return "";
  if (typeof x === "string") return x;
  try { return JSON.stringify(x, null, 2); } catch { return String(x); }
}

function postProcessMarkdown(t) {
  const s = asString(t);
  return s
    .replace(/VERSET (\d+)/g, "**VERSET $1**")
    .replace(/TEXTE BIBLIQUE\s*:/g, "**TEXTE BIBLIQUE :**")
    .replace(/EXPLICATION THÉOLOGIQUE\s*:/g, "**EXPLICATION THÉOLOGIQUE :**")
    .replace(/Introduction au Chapitre/g, "**Introduction au Chapitre**")
    .replace(/Synthèse Spirituelle/g, "**Synthèse Spirituelle**")
    .replace(/Principe Herméneutique/g, "**Principe Herméneutique**");
}

/* =========================
   Données statiques
========================= */

const BOOKS = [
  "Genèse", "Exode", "Lévitique", "Nombres", "Deutéronome",
  "Josué", "Juges", "Ruth", "1 Samuel", "2 Samuel", "1 Rois", "2 Rois",
  "1 Chroniques", "2 Chroniques", "Esdras", "Néhémie", "Esther",
  "Job", "Psaumes", "Proverbes", "Ecclésiaste", "Cantique des cantiques",
  "Ésaïe", "Jérémie", "Lamentations", "Ézéchiel", "Daniel",
  "Osée", "Joël", "Amos", "Abdias", "Jonas", "Michée", "Nahum", "Habacuc",
  "Sophonie", "Aggée", "Zacharie", "Malachie",
  "Matthieu", "Marc", "Luc", "Jean", "Actes",
  "Romains", "1 Corinthiens", "2 Corinthiens", "Galates", "Éphésiens",
  "Philippiens", "Colossiens", "1 Thessaloniciens", "2 Thessaloniciens",
  "1 Timothée", "2 Timothée", "Tite", "Philémon", "Hébreux",
  "Jacques", "1 Pierre", "2 Pierre", "1 Jean", "2 Jean", "3 Jean", "Jude",
  "Apocalypse"
];

const BOOK_CHAPTERS = {
  "Genèse": 50, "Exode": 40, "Lévitique": 27, "Nombres": 36, "Deutéronome": 34,
  "Josué": 24, "Juges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
  "1 Rois": 22, "2 Rois": 25, "1 Chroniques": 29, "2 Chroniques": 36,
  "Esdras": 10, "Néhémie": 13, "Esther": 10, "Job": 42, "Psaumes": 150,
  "Proverbes": 31, "Ecclésiaste": 12, "Cantique des cantiques": 8,
  "Ésaïe": 66, "Jérémie": 52, "Lamentations": 5, "Ézéchiel": 48, "Daniel": 12,
  "Osée": 14, "Joël": 3, "Amos": 9, "Abdias": 1, "Jonas": 4, "Michée": 7,
  "Nahum": 3, "Habacuc": 3, "Sophonie": 3, "Aggée": 2, "Zacharie": 14, "Malachie": 4,
  "Matthieu": 28, "Marc": 16, "Luc": 24, "Jean": 21, "Actes": 28,
  "Romains": 16, "1 Corinthiens": 16, "2 Corinthiens": 13, "Galates": 6,
  "Éphésiens": 6, "Philippiens": 4, "Colossiens": 4, "1 Thessaloniciens": 5,
  "2 Thessaloniciens": 3, "1 Timothée": 6, "2 Timothée": 4, "Tite": 3,
  "Philémon": 1, "Hébreux": 13, "Jacques": 5, "1 Pierre": 5, "2 Pierre": 3,
  "1 Jean": 5, "2 Jean": 1, "3 Jean": 1, "Jude": 1, "Apocalypse": 22
};

const BASE_RUBRIQUES = [
  "Étude verset par verset",
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
  "Plan d'action"
];

/* =========================
   Utilitaires fetch (fallbacks)
========================= */

// mapping endpoints (nouveau → legacy)
const ENDPOINTS = {
  verseProgressive: [
    "/generate-verse-by-verse-progressive",
    "/g_verse_progressive",
  ],
  verse: [
    "/generate-verse-by-verse",
    "/g_te-verse-by-verse",
  ],
  study: [
    "/generate-study",
    "/g_study_28",
  ],
  verseGemini: [
    "/generate-verse-by-verse-gemini",
    "/generate-verse-by-verse",
    "/g_te-verse-by-verse",
  ],
  studyGemini: [
    "/generate-study-gemini",
    "/generate-study",
    "/g_study_28",
  ],
};

async function smartPost(pathList, payload) {
  let lastErr = null;
  for (const p of pathList) {
    const url = `${API_BASE}${p}`;
    try {
      console.log("[API] POST →", url);
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload || {}),
      });
      if (r.ok) {
        const ct = r.headers.get("content-type") || "";
        if (ct.includes("application/json")) {
          return { data: await r.json(), url };
        }
        return { data: { raw: await r.text() }, url };
      }
      if (r.status === 404) { lastErr = new Error(`404 @ ${url}`); continue; }
      const bodyText = await r.text().catch(() => "");
      throw new Error(`HTTP ${r.status} @ ${url}${bodyText ? " – " + bodyText.slice(0, 300) : ""}`);
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error("Tous les endpoints ont échoué");
}

/* =========================
   Composant Principal App
========================= */

function App() {
  // États principaux
  const [selectedBook, setSelectedBook] = useState("--");
  const [selectedChapter, setSelectedChapter] = useState("--");
  const [selectedVerse, setSelectedVerse] = useState("--");
  const [selectedVersion, setSelectedVersion] = useState("LSG");
  const [selectedLength, setSelectedLength] = useState(500);
  const [activeRubrique, setActiveRubrique] = useState(0);
  const [content, setContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [rubriquesStatus, setRubriquesStatus] = useState({});
  const [currentTheme, setCurrentTheme] = useState(0);
  const [lastStudy, setLastStudy] = useState(null);
  const [progressPercent, setProgressPercent] = useState(0);
  const [searchQuery, setSearchQuery] = useState(""); // ← unique déclaration

  // États génération progressive
  const [isProgressiveLoading, setIsProgressiveLoading] = useState(false);
  const [currentBatchVerse, setCurrentBatchVerse] = useState(1);
  const [progressiveStats, setProgressiveStats] = useState(null);

  // Thèmes
  const colorThemes = [
    { name: "Violet Mystique", primary: "#667eea", secondary: "#764ba2", accent: "#667eea",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      headerBg: "linear-gradient(90deg, #3b4371 0%, #f093fb 50%, #f5576c 100%)" },
    { name: "Océan Profond", primary: "#0891b2", secondary: "#0284c7", accent: "#0891b2",
      background: "linear-gradient(135deg, #0891b2 0%, #0284c7 100%)",
      headerBg: "linear-gradient(90deg, #075985 0%, #0ea5e9 50%, #38bdf8 100%)" },
    { name: "Émeraude Vert", primary: "#10b981", secondary: "#059669", accent: "#10b981",
      background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
      headerBg: "linear-gradient(90deg, #064e3b 0%, #34d399 50%, #6ee7b7 100%)" },
    { name: "Rose Passion", primary: "#ec4899", secondary: "#db2777", accent: "#ec4899",
      background: "linear-gradient(135deg, #ec4899 0%, #db2777 100%)",
      headerBg: "linear-gradient(90deg, #831843 0%, #f472b6 50%, #f9a8d4 100%)" },
    { name: "Orange Sunset", primary: "#f59e0b", secondary: "#d97706", accent: "#f59e0b",
      background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
      headerBg: "linear-gradient(90deg, #92400e 0%, #fbbf24 50%, #fcd34d 100%)" },
    { name: "Indigo Royal", primary: "#6366f1", secondary: "#4f46e5", accent: "#6366f1",
      background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
      headerBg: "linear-gradient(90deg, #312e81 0%, #8b5cf6 50%, #c4b5fd 100%)" },
    { name: "Teal Tropical", primary: "#14b8a6", secondary: "#0f766e", accent: "#14b8a6",
      background: "linear-gradient(135deg, #14b8a6 0%, #0f766e 100%)",
      headerBg: "linear-gradient(90deg, #134e4a 0%, #5eead4 50%, #99f6e4 100%)" },
    { name: "Crimson Fire", primary: "#dc2626", secondary: "#b91c1c", accent: "#dc2626",
      background: "linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)",
      headerBg: "linear-gradient(90deg, #7f1d1d 0%, #f87171 50%, #fecaca 100%)" },
    { name: "Amber Gold", primary: "#f59e0b", secondary: "#d97706", accent: "#f59e0b",
      background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
      headerBg: "linear-gradient(90deg, #78350f 0%, #fbbf24 50%, #fef3c7 100%)" },
    { name: "Slate Modern", primary: "#64748b", secondary: "#475569", accent: "#64748b",
      background: "linear-gradient(135deg, #64748b 0%, #475569 100%)",
      headerBg: "linear-gradient(90deg, #1e293b 0%, #94a3b8 50%, #e2e8f0 100%)" },
    { name: "Lime Electric", primary: "#65a30d", secondary: "#4d7c0f", accent: "#65a30d",
      background: "linear-gradient(135deg, #65a30d 0%, #4d7c0f 100%)",
      headerBg: "linear-gradient(90deg, #365314 0%, #84cc16 50%, #d9f99d 100%)" },
    { name: "Fuchsia Magic", primary: "#c026d3", secondary: "#a21caf", accent: "#c026d3",
      background: "linear-gradient(135deg, #c026d3 0%, #a21caf 100%)",
      headerBg: "linear-gradient(90deg, #701a75 0%, #e879f9 50%, #f5d0fe 100%)" },
  ];

  // Options de chapitres
  const availableChapters = useMemo(() => {
    if (selectedBook === "--" || !BOOK_CHAPTERS[selectedBook]) return ["--"];
    const max = BOOK_CHAPTERS[selectedBook] || 1;
    return ["--", ...Array.from({ length: max }, (_, i) => i + 1)];
  }, [selectedBook]);

  // Charger/sauver dernière étude
  useEffect(() => {
    const saved = localStorage.getItem("lastBibleStudy");
    if (saved) { try { setLastStudy(JSON.parse(saved)); } catch(e){ console.error(e);} }
    const beforeUnload = () => saveCurrentStudy();
    window.addEventListener("beforeunload", beforeUnload);
    return () => window.removeEventListener("beforeunload", beforeUnload);
  }, []);

  // Appliquer thème au chargement
  useEffect(() => {
    setTimeout(() => { changePalette(); setCurrentTheme(0); }, 100);
  }, []);

  const saveCurrentStudy = () => {
    if (selectedBook !== "--" && selectedChapter !== "--") {
      const currentStudy = {
        book: selectedBook, chapter: selectedChapter, verse: selectedVerse,
        version: selectedVersion, length: selectedLength, activeRubrique,
        content, rubriquesStatus, timestamp: new Date().toISOString(),
        displayTitle: `${selectedBook} ${selectedChapter}${selectedVerse !== "--" ? ":" + selectedVerse : ""}`
      };
      localStorage.setItem("lastBibleStudy", JSON.stringify(currentStudy));
      setLastStudy(currentStudy);
    }
  };

  const restoreLastStudy = () => {
    if (!lastStudy) return;
    setSelectedBook(lastStudy.book);
    setSelectedChapter(lastStudy.chapter);
    setSelectedVerse(lastStudy.verse || "--");
    setSelectedVersion(lastStudy.version || "LSG");
    setSelectedLength(lastStudy.length || 500);
    setActiveRubrique(lastStudy.activeRubrique || 0);
    setContent(lastStudy.content || "");
    setRubriquesStatus(lastStudy.rubriquesStatus || {});
  };

  const rubriquesItems = BASE_RUBRIQUES.map((title, index) => ({ id: index, title }));

  /* =========================
     Gestionnaires
  ========================= */

  const handleBookChange = (e) => {
    saveCurrentStudy();
    const book = e.target.value;
    setSelectedBook(book);
    setSelectedChapter(book === "--" ? "--" : 1);
    setSelectedVerse("--");
  };

  const handleChapterChange = (e) => {
    saveCurrentStudy();
    const chapter = e.target.value;
    setSelectedChapter(chapter === "--" ? "--" : Number(chapter));
    setSelectedVerse("--");
  };

  const handleVerseChange = (e) => setSelectedVerse(e.target.value);
  const handleVersionChange = (e) => setSelectedVersion(e.target.value);
  const handleLengthChange = (e) => setSelectedLength(Number(e.target.value));

  // Recherche intelligente
  const parseSearchQuery = (query) => {
    if (!query.trim()) return null;
    const normalized = query.trim();
    const patterns = [/^(.+?)\s+(\d+):(\d+)$/, /^(.+?)\s+(\d+)$/, /^(.+)$/];
    for (const pat of patterns) {
      const m = normalized.match(pat);
      if (m) {
        const bookName = m[1].trim();
        const chapter = m[2] ? parseInt(m[2]) : null;
        const verse = m[3] ? parseInt(m[3]) : null;
        const found = BOOKS.find(b =>
          b.toLowerCase() === bookName.toLowerCase() ||
          b.toLowerCase().includes(bookName.toLowerCase()) ||
          bookName.toLowerCase().includes(b.toLowerCase())
        );
        if (found) return { book: found, chapter: chapter || 1, verse: verse || "--" };
      }
    }
    return null;
  };

  const handleSearchChange = (e) => {
    const q = e.target.value;
    setSearchQuery(q);
    const parsed = parseSearchQuery(q);
    if (parsed) {
      saveCurrentStudy();
      setSelectedBook(parsed.book);
      setSelectedChapter(parsed.chapter);
      setSelectedVerse(parsed.verse);
    }
  };

  // Progress bar
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const animateProgress = async (duration = 3000) => {
    setProgressPercent(0);
    const steps = 100, step = duration / steps;
    for (let i = 0; i <= steps; i++) { setProgressPercent(i); await wait(step); }
  };

  // YouVersion
  const openYouVersion = () => {
    if (selectedBook === "--") return alert("Veuillez d'abord sélectionner un livre de la Bible");
    const bookCodes = {"Genèse":"GEN","Exode":"EXO","Lévitique":"LEV","Nombres":"NUM","Deutéronome":"DEU","Josué":"JOS","Juges":"JDG","Ruth":"RUT","1 Samuel":"1SA","2 Samuel":"2SA","1 Rois":"1KI","2 Rois":"2KI","1 Chroniques":"1CH","2 Chroniques":"2CH","Esdras":"EZR","Néhémie":"NEH","Esther":"EST","Job":"JOB","Psaumes":"PSA","Proverbes":"PRO","Ecclésiaste":"ECC","Cantique des cantiques":"SNG","Ésaïe":"ISA","Jérémie":"JER","Lamentations":"LAM","Ézéchiel":"EZK","Daniel":"DAN","Osée":"HOS","Joël":"JOL","Amos":"AMO","Abdias":"OBA","Jonas":"JON","Michée":"MIC","Nahum":"NAM","Habacuc":"HAB","Sophonie":"ZEP","Aggée":"HAG","Zacharie":"ZEC","Malachie":"MAL","Matthieu":"MAT","Marc":"MRK","Luc":"LUK","Jean":"JHN","Actes":"ACT","Romains":"ROM","1 Corinthiens":"1CO","2 Corinthiens":"2CO","Galates":"GAL","Éphésiens":"EPH","Philippiens":"PHP","Colossiens":"COL","1 Thessaloniciens":"1TH","2 Thessaloniciens":"2TH","1 Timothée":"1TI","2 Timothée":"2TI","Tite":"TIT","Philémon":"PHM","Hébreux":"HEB","Jacques":"JAS","1 Pierre":"1PE","2 Pierre":"2PE","1 Jean":"1JN","2 Jean":"2JN","3 Jean":"3JN","Jude":"JUD","Apocalypse":"REV"};
    const code = bookCodes[selectedBook]; if (!code) return alert("Livre non reconnu pour YouVersion");
    let url = `https://www.bible.com/fr/bible/63/${code}`;
    if (selectedChapter !== "--") { url += `.${selectedChapter}`; if (selectedVerse !== "--") url += `.${selectedVerse}`; }
    window.open(url, "_blank");
  };

  const handleReset = () => {
    saveCurrentStudy();
    setSelectedBook("--"); setSelectedChapter("--"); setSelectedVerse("--");
    setSelectedVersion("LSG"); setSelectedLength(500); setActiveRubrique(0);
    setContent(""); setRubriquesStatus({});
    setProgressiveStats(null);
  };

  const handleRubriqueSelect = (id) => {
    setActiveRubrique(id);
    if (rubriquesStatus[id] === "completed") setContent(`Contenu de la rubrique ${id}: ${getRubTitle(id)}`);
    else setContent("");
  };

  // Palette (reprend ta logique initiale)
  const changePalette = () => {
    const nextTheme = (currentTheme + 1) % colorThemes.length;
    setCurrentTheme(nextTheme);
    const theme = colorThemes[nextTheme];

    const app = document.querySelector('.App');
    if (app) app.style.background = theme.background;

    const header = document.querySelector('.header-banner');
    if (header) header.style.background = theme.headerBg;

    document.documentElement.style.setProperty('--theme-primary', theme.primary);
    document.documentElement.style.setProperty('--theme-secondary', theme.secondary);
    document.documentElement.style.setProperty('--theme-accent', theme.accent);

    const progressPill = document.querySelector('.progress-pill');
    if (progressPill) progressPill.style.background = theme.primary;

    const contentHeader = document.querySelector('.content-header');
    if (contentHeader)
      contentHeader.style.background = `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})`;

    const btnReset = document.querySelector('.btn-reset');
    if (btnReset) { btnReset.style.background = theme.secondary; btnReset.style.color = 'white'; btnReset.style.border = 'none'; }

    const btnPalette = document.querySelector('.btn-palette');
    if (btnPalette) { btnPalette.style.background = theme.primary; btnPalette.style.color = 'white'; btnPalette.style.border = 'none'; }

    const btnLastStudy = document.querySelector('.btn-last-study');
    if (btnLastStudy) {
      btnLastStudy.style.background = `linear-gradient(135deg, ${theme.primary}, ${theme.secondary})`;
      btnLastStudy.style.color = 'white'; btnLastStudy.style.border = 'none';
    }

    const btnGemini = document.querySelector('.btn-gemini');
    if (btnGemini) { btnGemini.style.background = `linear-gradient(90deg, ${theme.secondary}, ${theme.accent})`; btnGemini.style.color = 'white'; btnGemini.style.border = 'none'; }

    const btnVersets = document.querySelector('.btn-versets-prog');
    if (btnVersets) { btnVersets.style.background = theme.accent; btnVersets.style.color = 'white'; btnVersets.style.border = 'none'; }

    const btnGenerate = document.querySelector('.btn-generate');
    if (btnGenerate) { btnGenerate.style.background = `linear-gradient(45deg, ${theme.primary}, ${theme.secondary})`; btnGenerate.style.color = 'white'; btnGenerate.style.border = 'none'; }

    const btnValidate = document.querySelector('.btn-validate');
    if (btnValidate) { btnValidate.style.background = theme.primary; btnValidate.style.color = 'white'; btnValidate.style.border = 'none'; }
  };

  /* =========================
     Génération (avec fallbacks)
  ========================= */

  const generateVerseByVerseProgressive = async () => {
    try {
      setIsLoading(true); setIsProgressiveLoading(true);
      setContent(""); setProgressPercent(0);
      setRubriquesStatus(p => ({ ...p, 0: "in-progress" }));
      setProgressiveStats(null);

      const passage = (selectedVerse === "--" || selectedVerse === "vide")
        ? `${selectedBook} ${selectedChapter}`
        : `${selectedBook} ${selectedChapter}:${selectedVerse}`;

      let accumulated = "", hasMore = true, nextStartVerse = 1;
      let totalVerses = 0, processedVerses = 0;

      while (hasMore) {
        const { data, url } = await smartPost(ENDPOINTS.verseProgressive, {
          passage, 
          version: selectedVersion, 
          batch_size: nextStartVerse === 1 ? 5 : 3, // 5 premiers versets rapidement, puis 3 par batch
          start_verse: nextStartVerse,
          priority_mode: nextStartVerse === 1 // Mode priorité pour les 5 premiers
        });
        console.log("[API OK]", url);

        accumulated += data.batch_content || "";
        setContent(formatContent(accumulated));
        setProgressPercent(Math.round(data.total_progress || 0));

        // Mise à jour des stats
        if (data.verse_stats) {
          setProgressiveStats({
            processed: data.verse_stats.processed,
            total: data.verse_stats.total,
            current_batch: data.verse_range,
            speed: nextStartVerse === 1 ? "Rapide ⚡" : "Standard"
          });
        }

        hasMore = !!data.has_more;
        nextStartVerse = data.next_start_verse || nextStartVerse + (nextStartVerse === 1 ? 5 : 3);
        setCurrentBatchVerse(nextStartVerse);

        // Délai réduit pour les 5 premiers versets
        await wait(nextStartVerse <= 6 ? 200 : 400);
      }

      setRubriquesStatus(p => ({ ...p, 0: "completed" }));
      setProgressPercent(100);
      setProgressiveStats(prev => prev ? {...prev, speed: "Terminé ✅"} : null);
    } catch (err) {
      console.error("Erreur génération progressive:", err);
      setContent(`Erreur lors de la génération: ${err.message}`);
      setRubriquesStatus(p => ({ ...p, 0: "error" }));
    } finally {
      setIsLoading(false); setIsProgressiveLoading(false);
    }
  };

  const generateWithGemini = async () => {
    try {
      setIsLoading(true); setContent("Génération avec Gemini enrichie en cours...");
      setRubriquesStatus(p => ({ ...p, [activeRubrique]: "in-progress" }));

      const passage = (selectedVerse === "--" || selectedVerse === "vide")
        ? `${selectedBook} ${selectedChapter}`
        : `${selectedBook} ${selectedChapter}:${selectedVerse}`;

      const pathList = activeRubrique === 0 ? ENDPOINTS.verseGemini : ENDPOINTS.studyGemini;
      const payload = activeRubrique === 0
        ? { passage, version: selectedVersion, requestedRubriques: [0], enriched: true }
        : { passage, version: selectedVersion, requestedRubriques: [activeRubrique], enriched: true };

      const { data, url } = await smartPost(pathList, payload);
      console.log("[API OK]", url);

      setContent(postProcessMarkdown(data.content || "Aucun contenu généré"));
      setRubriquesStatus(p => ({ ...p, [activeRubrique]: "completed" }));
    } catch (err) {
      console.error("Erreur Gemini:", err);
      setContent(`Erreur Gemini: ${err.message}`);
      setRubriquesStatus(p => ({ ...p, [activeRubrique]: undefined }));
    } finally { setIsLoading(false); }
  };

  const generate28Points = async () => {
    try {
      setIsLoading(true); setContent("Génération étude 28 points en cours...");
      animateProgress(4000);

      const inProgress = {}; BASE_RUBRIQUES.forEach((_, i) => inProgress[i] = "in-progress");
      setRubriquesStatus(inProgress);

      const passage = (selectedVerse === "--" || selectedVerse === "vide")
        ? `${selectedBook} ${selectedChapter}`
        : `${selectedBook} ${selectedChapter}:${selectedVerse}`;

      const { data, url } = await smartPost(ENDPOINTS.study, {
        passage, version: selectedVersion, tokens: selectedLength, enriched: true
      });
      console.log("[API OK]", url);

      setContent(postProcessMarkdown(data.content || "Aucun contenu généré"));
      const completed = {}; BASE_RUBRIQUES.forEach((_, i) => completed[i] = "completed");
      setRubriquesStatus(completed);
    } catch (err) {
      console.error("Erreur génération 28 points:", err);
      setContent(`Erreur: ${err.message}`);
      setRubriquesStatus({});
    } finally { setIsLoading(false); }
  };

  /* =========================
     Formatage du contenu
  ========================= */

  const formatContent = (text) => {
    if (!text) return "";
    const isVxV = text.includes("VERSET") && text.includes("TEXTE BIBLIQUE") && text.includes("EXPLICATION THÉOLOGIQUE");
    if (isVxV) return formatVerseByVerseContent(text);
    return text
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/^\# (.*$)/gim, "<h1>$1</h1>")
      .replace(/^\## (.*$)/gim, "<h2>$1</h2>")
      .replace(/^\### (.*$)/gim, "<h3>$1</h3>")
      .split("\n\n")
      .map(p => (p.trim() ? `<p>${p.replace(/\n/g, "<br>")}</p>` : ""))
      .join("");
  };

  const formatVerseByVerseContent = (text) => {
    const sections = text.split(/VERSET (\d+)/);
    let html = '<div class="verse-study-container">';

    if (sections[0]) {
      const intro = sections[0]
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/^\### (.*$)/gim, "<h3>$1</h3>")
        .replace(/^\## (.*$)/gim, "<h2>$1</h2>")
        .replace(/^\# (.*$)/gim, "<h1>$1</h1>");
      html += `<div style="margin-bottom: 30px;">${intro.replace(/\n/g, "<br>")}</div>`;
    }

    for (let i = 1; i < sections.length; i += 2) {
      const verseNumber = sections[i];
      const block = sections[i + 1];

      if (block) {
        html += `<div class="verse-block">
          <div class="verse-header">VERSET ${verseNumber}</div>`;

        const parts = block.split(/TEXTE BIBLIQUE\s*:/);
        if (parts.length > 1) {
          const afterBiblical = parts[1].split(/EXPLICATION THÉOLOGIQUE\s*:/);
          const biblicalText = (afterBiblical[0] || "").trim();
          const theologicalExplanation = afterBiblical[1] ? afterBiblical[1].trim() : "";

          html += `
            <div class="section-label biblical-label">📖 TEXTE BIBLIQUE</div>
            <div class="biblical-text">${biblicalText.replace(/\n/g, "<br>")}</div>`;

          if (theologicalExplanation) {
            html += `
              <div class="section-label theological-label">🎓 EXPLICATION THÉOLOGIQUE</div>
              <div class="theological-explanation">${theologicalExplanation.replace(/\n/g, "<br>")}</div>`;
          }
        }

        html += "</div>";
      }
    }

    html += "</div>";
    return html;
  };

  /* =========================
     Rendu (UI intacte)
  ========================= */

  return (
    <div className="App">
      {/* Header avec texte défilant */}
      <header className="header-banner">
        <div className="scroll-text">
          ✨ MÉDITATION BIBLIQUE ✨ ÉTUDE SPIRITUELLE ✨ SAGESSE DIVINE ✨ MÉDITATION THÉOLOGIQUE ✨ CONTEMPLATION SACRÉE ✨ RÉFLEXION INSPIRÉE ✨
        </div>
      </header>

      {/* Indicateur de progression centré */}
      <div className="progress-container">
        <div className="progress-pill">
          {progressPercent}%
          {isProgressiveLoading && progressiveStats && (
            <span className="progressive-indicator">
              ⚡ {progressiveStats.speed} - {progressiveStats.current_batch} ({progressiveStats.processed}/{progressiveStats.total})
            </span>
          )}
        </div>
      </div>

      {/* Interface principale */}
      <div className="main-container">
        {/* Section de recherche */}
        <div className="search-section">
          <div className="search-input">
            <input
              type="text"
              placeholder="Rechercher (ex : Marc 5:1, 1 Jean 2, Genèse 1:1-5)"
              className="search-field"
              value={searchQuery}
              onChange={handleSearchChange}
            />
          </div>

          <div className="controls-row">
            <SelectPill label="Livre" value={selectedBook} options={["--", ...BOOKS]} onChange={handleBookChange} />
            <SelectPill label="Chapitre" value={selectedChapter} options={availableChapters} onChange={handleChapterChange} />
            <button className="btn-validate" disabled={isLoading}>Valider</button>
            <SelectPill label="Verset" value={selectedVerse} options={["--", ...Array.from({ length: 50 }, (_, i) => i + 1)]} onChange={handleVerseChange} />
            <SelectPill label="Version" value={selectedVersion} options={["LSG", "Darby", "NEG"]} onChange={handleVersionChange} />
            <SelectPill label="Longueur" value={selectedLength} options={[300, 500, 1000, 2000]} onChange={handleLengthChange} />
            <button className="btn-read" onClick={openYouVersion}>Lire la Bible</button>
            <button className="btn-chat">ChatGPT</button>
          </div>

          {/* Boutons d'action */}
          <div className="action-buttons">
            <button className="btn-reset" onClick={handleReset}>🔄 Reset</button>
            <button className="btn-palette" onClick={changePalette}>🎨 {colorThemes[currentTheme].name}</button>
            <button className="btn-last-study" onClick={restoreLastStudy} disabled={!lastStudy}
              title={lastStudy ? `Restaurer: ${lastStudy.book} ${lastStudy.chapter}${lastStudy.verse !== "--" ? ":" + lastStudy.verse : ""}` : "Aucune étude sauvegardée"}>
              {lastStudy ? `📖 ${lastStudy.book} ${lastStudy.chapter}${lastStudy.verse !== "--" ? ":" + lastStudy.verse : ""}` : "📖 Dernière étude"}
            </button>
            <button className={`btn-gemini ${isLoading ? "loading" : ""}`} onClick={generateWithGemini} disabled={isLoading}>🤖 Gemini Flash</button>
            <button className="btn-versets-prog" onClick={generateVerseByVerseProgressive} disabled={isLoading} title="Analyse progressive enrichie - 5 premiers versets rapides">⚡ Versets Prog</button>
            <button className="btn-generate" onClick={generate28Points} disabled={isLoading}>Générer</button>
          </div>
        </div>

        {/* Layout 2 colonnes */}
        <div className="three-column-layout" style={{ gridTemplateColumns: "300px 1fr" }}>
          {/* Colonne gauche - Rubriques */}
          <div className="left-column">
            <h3>Rubriques (29)</h3>
            <RubriquesInline items={rubriquesItems} activeId={activeRubrique} onSelect={handleRubriqueSelect} rubriquesStatus={rubriquesStatus} />
          </div>

          {/* Colonne centrale - Contenu */}
          <div className="center-column">
            <div className="content-header">
              <h2>{`${activeRubrique}. ${getRubTitle(activeRubrique)}`}</h2>
              <div className="nav-buttons">
                <button onClick={() => setActiveRubrique(Math.max(0, activeRubrique - 1))} disabled={activeRubrique === 0}>◀ Précédent</button>
                <button onClick={() => setActiveRubrique(Math.min(BASE_RUBRIQUES.length - 1, activeRubrique + 1))} disabled={activeRubrique === BASE_RUBRIQUES.length - 1}>Suivant ▶</button>
              </div>
            </div>

            <div className="content-area">
              {isLoading ? (
                <div className="loading-container">
                  <div className="loading-spinner"></div>
                  <p>Génération en cours...</p>
                  {progressiveStats && (
                    <div className="progressive-stats">
                      <p>📊 Versets traités: {progressiveStats.processed}/{progressiveStats.total}</p>
                      <p>🎯 Batch actuel: {progressiveStats.current_batch}</p>
                      <p>⚡ Mode: {progressiveStats.speed}</p>
                    </div>
                  )}
                </div>
              ) : content ? (
                <div className="content-text" dangerouslySetInnerHTML={{ __html: formatContent(content) }} />
              ) : (
                <div className="welcome-section">
                  <h1>🙏 Bienvenue dans votre Espace d'Étude</h1>
                  <p>Cet outil vous accompagne dans une méditation biblique structurée et claire.</p>
                  <p><strong>Nouveau:</strong> Le bouton "Versets Prog" génère rapidement les 5 premiers versets puis continue progressivement!</p>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

/* =========================
   Composants auxiliaires
========================= */

function getRubTitle(index) {
  return BASE_RUBRIQUES[index] || `Rubrique ${index}`;
}

function SelectPill({ label, value, options, onChange }) {
  return (
    <div className="select-pill">
      <label>{label}</label>
      <select value={value} onChange={onChange}>
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

export default App;