/* eslint-disable */
import React, { useState, useEffect, useMemo } from "react";
import "./App.css";
import "./rubriques.css";

/* =========================
   Backend URL
========================= */

const getBackendUrl = () => {
  const raw = (process.env.REACT_APP_BACKEND_URL || "").trim();
  const cleaned = raw.replace(/^["']|["']$/g, "").replace(/\/+$/g, "");
  if (cleaned) return cleaned;

  const hostname = typeof window !== "undefined" ? window.location.hostname : "";
  if (hostname === "localhost" || hostname === "127.0.0.1") return "http://localhost:8001";
  return "https://etude8-bible-api-production.up.railway.app";
};

const BACKEND_URL = getBackendUrl();
const API_BASE = `${BACKEND_URL.replace(/\/+$/g, "")}/api`;

if (typeof window !== "undefined") {
  console.log("[App] BACKEND_URL =", BACKEND_URL);
  console.log("[App] API_BASE     =", API_BASE);
}

/* =========================
   Utils
========================= */
function asString(x) {
  if (x === undefined || x === null) return "";
  if (typeof x === "string") return x;
  try { return JSON.stringify(x, null, 2); } catch { return String(x); }
}

// ⚠️ NE PAS styliser "VERSET n" ici (on s’en sert pour découper)
function postProcessLabels(t) {
  const s = asString(t);
  return s
    .replace(/TEXTE BIBLIQUE\s*:/g, "TEXTE BIBLIQUE :")
    .replace(/EXPLICATION THÉOLOGIQUE\s*:/g, "EXPLICATION THÉOLOGIQUE :");
}

/* =========================
   Formatage pour rubrique 0
========================= */

// Rend un HTML riche, bloc par bloc, à partir du RAW backend
function formatVerseByVerseContent(rawText) {
  if (!rawText) return "";

  const text = postProcessLabels(rawText);

  // IMPORTANT: en JS on met les flags après le /, pas (?m)
  // On coupe sur chaque "VERSET n" en conservant les numéros capturés
  const sections = text.split(/^VERSET\s+(\d+)\s*$/gm);
  // sections = [intro, num1, bloc1, num2, bloc2, ...]

  let html = '<div class="verse-study-container">';

  // Intro si présente
  if (sections[0] && sections[0].trim()) {
    const intro = sections[0]
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/^\### (.*$)/gim, "<h3>$1</h3>")
      .replace(/^\## (.*$)/gim, "<h2>$1</h2>")
      .replace(/^\# (.*$)/gim, "<h1>$1</h1>");
    html += `<div class="intro-block">${intro.replace(/\n/g, "<br>")}</div>`;
  }

  // Parcours versets
  for (let i = 1; i < sections.length; i += 2) {
    const verseNumber = sections[i];
    const block = (sections[i + 1] || "").trim();
    if (!verseNumber) continue;

    html += `
      <div class="verse-block">
        <div class="verse-header">📚 VERSET ${verseNumber}</div>
    `;

    // Découpe interne: TEXTE BIBLIQUE / EXPLICATION THÉOLOGIQUE
    const tbSplit = block.split(/^TEXTE BIBLIQUE\s*:\s*$/m);
    if (tbSplit.length > 1) {
      const afterBiblical = tbSplit[1].split(/^EXPLICATION THÉOLOGIQUE\s*:\s*$/m);
      const biblicalText = (afterBiblical[0] || "").trim();
      const theologicalExplanation = (afterBiblical[1] || "").trim();

      html += `
        <div class="section-label biblical-label">📜 TEXTE BIBLIQUE :</div>
        <div class="biblical-text">${biblicalText.replace(/\n/g, "<br>")}</div>
      `;

      if (theologicalExplanation) {
        html += `
          <div class="section-label theological-label">🎓 EXPLICATION THÉOLOGIQUE :</div>
          <div class="theological-explanation">${theologicalExplanation.replace(/\n/g, "<br>")}</div>
        `;
      }
    } else if (block) {
      // fallback si le bloc n’a pas les 2 labels
      html += `<div class="biblical-text">${block.replace(/\n/g, "<br>")}</div>`;
    }

    html += `</div>`; // .verse-block
  }

  html += `</div>`; // .verse-study-container
  return html;
}

/* =========================
   Données
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

/* =========================
   API util
========================= */

const ENDPOINTS = {
  verseGemini: [
    "/generate-verse-by-verse-gemini",
    "/generate-verse-by-verse",
    "/g_te-verse-by-verse",
  ],
  verse: [
    "/generate-verse-by-verse",
    "/g_te-verse-by-verse",
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
        headers: { "Content-Type": "application/json; charset=utf-8" },
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
   App (rubrique 0)
========================= */

export default function App() {
  const [selectedBook, setSelectedBook] = useState("Genèse");
  const [selectedChapter, setSelectedChapter] = useState(1);
  const [selectedVerse, setSelectedVerse] = useState("--");
  const [selectedVersion, setSelectedVersion] = useState("LSG");
  const [selectedLength, setSelectedLength] = useState(1500); // 500 / 1500 / 2500

  const [isLoading, setIsLoading] = useState(false);
  const [contentRaw, setContentRaw] = useState("");
  const [progressPercent, setProgressPercent] = useState(0);

  const availableChapters = useMemo(() => {
    if (!BOOK_CHAPTERS[selectedBook]) return ["--"];
    const max = BOOK_CHAPTERS[selectedBook] || 1;
    return ["--", ...Array.from({ length: max }, (_, i) => i + 1)];
  }, [selectedBook]);

  const LENGTH_OPTIONS = [500, 1500, 2500];
  const handleLengthChange = (e) => {
    const v = Number(e.target.value);
    if (v <= 500) setSelectedLength(500);
    else if (v <= 1500) setSelectedLength(1500);
    else setSelectedLength(2500);
  };

  const generateRubrique0 = async () => {
    try {
      setIsLoading(true);
      setProgressPercent(0);
      setContentRaw("");

      const passage = (selectedVerse === "--" || selectedVerse === "vide")
        ? `${selectedBook} ${selectedChapter}`
        : `${selectedBook} ${selectedChapter}:${selectedVerse}`;

      // Essaye gemini → fallback standard
      let data, url;
      try {
        ({ data, url } = await smartPost(ENDPOINTS.verseGemini, {
          passage, version: selectedVersion, enriched: true, target_chars: selectedLength
        }));
        console.log("[API OK Gemini]", url);
      } catch (e) {
        console.warn("[Gemini fallback]", e?.message || e);
        ({ data, url } = await smartPost(ENDPOINTS.verse, {
          passage, version: selectedVersion, enriched: true, target_chars: selectedLength
        }));
        console.log("[API OK Standard]", url);
      }

      const raw = data?.content || "";
      console.log("[RAW length]", raw.length);
      setContentRaw(raw);
      setProgressPercent(100);
    } catch (err) {
      console.error("Erreur génération:", err);
      setContentRaw(`ERREUR: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const html = formatVerseByVerseContent(contentRaw);

  return (
    <div className="App">
      <header className="header-banner">
        <div className="scroll-text">✨ Étude verset par verset (Rubrique 0) ✨</div>
      </header>

      <div className="progress-container">
        <div className="progress-pill">{progressPercent}%</div>
      </div>

      <div className="main-container">
        <div className="search-section">
          <div className="controls-row">
            <SelectPill label="Livre" value={selectedBook} options={BOOKS} onChange={(e)=>setSelectedBook(e.target.value)} />
            <SelectPill label="Chapitre" value={selectedChapter} options={["--", ...Array.from({length: BOOK_CHAPTERS[selectedBook]||1}, (_,i)=>i+1)]} onChange={(e)=>setSelectedChapter(Number(e.target.value))} />
            <SelectPill label="Verset" value={selectedVerse} options={["--", ...Array.from({ length: 50 }, (_, i) => i + 1)]} onChange={(e)=>setSelectedVerse(e.target.value)} />
            <SelectPill label="Version" value={selectedVersion} options={["LSG","Darby","NEG"]} onChange={(e)=>setSelectedVersion(e.target.value)} />
            <SelectPill label="Longueur" value={selectedLength} options={LENGTH_OPTIONS} onChange={handleLengthChange} />
            <button className="btn-generate" onClick={generateRubrique0} disabled={isLoading}>Générer Rubrique 0</button>
          </div>
        </div>

        <div className="three-column-layout" style={{ gridTemplateColumns: "1fr" }}>
          <div className="center-column">
            <div className="content-header">
              <h2>0. Étude verset par verset</h2>
            </div>

            <div className="content-area">
              {isLoading ? (
                <div className="loading-container">
                  <div className="loading-spinner"></div>
                  <p>Génération en cours…</p>
                </div>
              ) : html ? (
                <div className="content-text" dangerouslySetInnerHTML={{ __html: html }} />
              ) : (
                <div className="welcome-section">
                  <h1>Bienvenue 👋</h1>
                  <p>Choisis un passage puis clique sur <strong>Générer Rubrique 0</strong>.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============== UI bits ============== */
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
