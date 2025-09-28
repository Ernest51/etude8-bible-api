/* eslint-disable */
import React, { useState, useMemo } from "react";
import "./App.css";           // tu peux garder tes styles existants
import "./rubriques.css";

/* =========================
   Helpers & config
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

const ENDPOINTS = {
  // on tente d’abord Gemini puis fallback
  verseGeminiFirst: [
    "/generate-verse-by-verse-gemini",
    "/generate-verse-by-verse",
    "/g_te-verse-by-verse",
  ],
  verseProgressiveGeminiFirst: [
    "/generate-verse-by-verse-progressive-gemini",
    "/generate-verse-by-verse-progressive",
    "/g_verse_progressive",
  ],
};

async function smartPost(pathList, payload) {
  let lastErr = null;
  for (const p of pathList) {
    const url = `${API_BASE}${p}`;
    try {
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify(payload || {}),
      });
      if (r.ok) {
        const ct = r.headers.get("content-type") || "";
        if (ct.includes("application/json")) return { data: await r.json(), url };
        return { data: { raw: await r.text() }, url };
      }
      if (r.status === 404) { lastErr = new Error(`404 @ ${url}`); continue; }
      const txt = await r.text().catch(() => "");
      throw new Error(`HTTP ${r.status} @ ${url}${txt ? " – " + txt.slice(0, 300) : ""}`);
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error("Tous les endpoints ont échoué");
}

const BOOKS = [
  "Genèse","Exode","Lévitique","Nombres","Deutéronome","Josué","Juges","Ruth",
  "1 Samuel","2 Samuel","1 Rois","2 Rois","1 Chroniques","2 Chroniques","Esdras",
  "Néhémie","Esther","Job","Psaumes","Proverbes","Ecclésiaste","Cantique des cantiques",
  "Ésaïe","Jérémie","Lamentations","Ézéchiel","Daniel","Osée","Joël","Amos","Abdias",
  "Jonas","Michée","Nahum","Habacuc","Sophonie","Aggée","Zacharie","Malachie",
  "Matthieu","Marc","Luc","Jean","Actes","Romains","1 Corinthiens","2 Corinthiens",
  "Galates","Éphésiens","Philippiens","Colossiens","1 Thessaloniciens","2 Thessaloniciens",
  "1 Timothée","2 Timothée","Tite","Philémon","Hébreux","Jacques","1 Pierre","2 Pierre",
  "1 Jean","2 Jean","3 Jean","Jude","Apocalypse"
];

const BOOK_CHAPTERS = {
  "Genèse":50,"Exode":40,"Lévitique":27,"Nombres":36,"Deutéronome":34,"Josué":24,"Juges":21,"Ruth":4,
  "1 Samuel":31,"2 Samuel":24,"1 Rois":22,"2 Rois":25,"1 Chroniques":29,"2 Chroniques":36,"Esdras":10,
  "Néhémie":13,"Esther":10,"Job":42,"Psaumes":150,"Proverbes":31,"Ecclésiaste":12,"Cantique des cantiques":8,
  "Ésaïe":66,"Jérémie":52,"Lamentations":5,"Ézéchiel":48,"Daniel":12,"Osée":14,"Joël":3,"Amos":9,"Abdias":1,
  "Jonas":4,"Michée":7,"Nahum":3,"Habacuc":3,"Sophonie":3,"Aggée":2,"Zacharie":14,"Malachie":4,
  "Matthieu":28,"Marc":16,"Luc":24,"Jean":21,"Actes":28,"Romains":16,"1 Corinthiens":16,"2 Corinthiens":13,
  "Galates":6,"Éphésiens":6,"Philippiens":4,"Colossiens":4,"1 Thessaloniciens":5,"2 Thessaloniciens":3,
  "1 Timothée":6,"2 Timothée":4,"Tite":3,"Philémon":1,"Hébreux":13,"Jacques":5,"1 Pierre":5,"2 Pierre":3,
  "1 Jean":5,"2 Jean":1,"3 Jean":1,"Jude":1,"Apocalypse":22
};

const LENGTH_OPTIONS = [500, 1500, 2500];

const asString = (x) => {
  if (x === undefined || x === null) return "";
  if (typeof x === "string") return x;
  try { return JSON.stringify(x, null, 2); } catch { return String(x); }
};

// ne pas bold “VERSET n” (on stylise seulement les labels)
function postProcessLabels(t) {
  const s = asString(t);
  return s
    .replace(/TEXTE BIBLIQUE\s*:/g, "**TEXTE BIBLIQUE :**")
    .replace(/EXPLICATION THÉOLOGIQUE\s*:/g, "**EXPLICATION THÉOLOGIQUE :**")
    .replace(/Étude Verset par Verset\s*-\s*/g, "**Étude Verset par Verset - **");
}

function formatHtml(text) {
  if (!text) return "";
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/^# (.*)$/gim, "<h1>$1</h1>")
    .replace(/^## (.*)$/gim, "<h2>$1</h2>")
    .replace(/^### (.*)$/gim, "<h3>$1</h3>")
    .replace(/^VERSET\s+(\d+)\s*$/gim, "<h2 class='verset-header'>📖 VERSET $1</h2>")
    .replace(/^TEXTE BIBLIQUE\s*:$/gim, "<h4 class='texte-biblique-label'>📜 TEXTE BIBLIQUE :</h4>")
    .replace(/^EXPLICATION THÉOLOGIQUE\s*:$/gim, "<h4 class='explication-label'>🎓 EXPLICATION THÉOLOGIQUE :</h4>")
    .split("\n\n")
    .map(p => (p.trim() ? `<p>${p.replace(/\n/g, "<br>")}</p>` : ""))
    .join("");
}

/* =========================
   App (rubrique 0 only)
========================= */
export default function App() {
  const [book, setBook] = useState("Genèse");
  const [chapter, setChapter] = useState(1);
  const [verse, setVerse] = useState("--");
  const [version, setVersion] = useState("LSG");
  const [targetChars, setTargetChars] = useState(500);

  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState("");
  const [progressInfo, setProgressInfo] = useState(null);

  const chapters = useMemo(() => {
    const max = BOOK_CHAPTERS[book] || 1;
    return ["--", ...Array.from({ length: max }, (_, i) => i + 1)];
  }, [book]);

  const passageStr = () =>
    verse === "--" ? `${book} ${chapter}` : `${book} ${chapter}:${verse}`;

  async function generateFull() {
    try {
      setLoading(true);
      setContent("");
      setProgressInfo(null);

      const { data, url } = await smartPost(ENDPOINTS.verseGeminiFirst, {
        passage: passageStr(),
        version,
        enriched: true,
        target_chars: targetChars,
      });
      console.log("[FULL OK]", url);

      const styled = postProcessLabels(data.content || "Aucun contenu généré");
      setContent(styled);
    } catch (e) {
      setContent(`Erreur: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }

  // “progressif” = on appelle l’endpoint non-stream, mais on affiche par lignes
  async function generateProgressive() {
    try {
      setLoading(true);
      setContent("");
      setProgressInfo({ processed: 0, total: 0, current: "Préparation…" });

      const { data, url } = await smartPost(ENDPOINTS.verseGeminiFirst, {
        passage: passageStr(),
        version,
        enriched: true,
        target_chars: targetChars,
      });
      console.log("[PROG OK]", url);

      const raw = data.content || "";
      const totalVersets = (raw.match(/^VERSET\s+\d+\s*$/gm) || []).length;
      setProgressInfo((p) => ({ ...p, total: totalVersets, current: "Lecture…" }));

      const lines = raw.split("\n");
      let acc = "";
      let seenVersets = 0;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        acc += line + "\n";

        if (/^VERSET\s+\d+\s*$/.test(line)) {
          seenVersets++;
          setProgressInfo({ processed: seenVersets, total: totalVersets, current: line.trim() });
        }

        const styled = postProcessLabels(acc);
        setContent(styled);

        // petite pause visuelle
        await new Promise((r) => setTimeout(r, seenVersets <= 3 ? 40 : 120));
      }

      setProgressInfo((p) => p && { ...p, current: "Terminé ✅" });
    } catch (e) {
      setContent(`Erreur: ${e.message}`);
      setProgressInfo(null);
    } finally {
      setLoading(false);
    }
  }

  function openYouVersion() {
    const codes = {"Genèse":"GEN","Exode":"EXO","Lévitique":"LEV","Nombres":"NUM","Deutéronome":"DEU","Josué":"JOS","Juges":"JDG","Ruth":"RUT","1 Samuel":"1SA","2 Samuel":"2SA","1 Rois":"1KI","2 Rois":"2KI","1 Chroniques":"1CH","2 Chroniques":"2CH","Esdras":"EZR","Néhémie":"NEH","Esther":"EST","Job":"JOB","Psaumes":"PSA","Proverbes":"PRO","Ecclésiaste":"ECC","Cantique des cantiques":"SNG","Ésaïe":"ISA","Jérémie":"JER","Lamentations":"LAM","Ézéchiel":"EZK","Daniel":"DAN","Osée":"HOS","Joël":"JOL","Amos":"AMO","Abdias":"OBA","Jonas":"JON","Michée":"MIC","Nahum":"NAM","Habacuc":"HAB","Sophonie":"ZEP","Aggée":"HAG","Zacharie":"ZEC","Malachie":"MAL","Matthieu":"MAT","Marc":"MRK","Luc":"LUK","Jean":"JHN","Actes":"ACT","Romains":"ROM","1 Corinthiens":"1CO","2 Corinthiens":"2CO","Galates":"GAL","Éphésiens":"EPH","Philippiens":"PHP","Colossiens":"COL","1 Thessaloniciens":"1TH","2 Thessaloniciens":"2TH","1 Timothée":"1TI","2 Timothée":"2TI","Tite":"TIT","Philémon":"PHM","Hébreux":"HEB","Jacques":"JAS","1 Pierre":"1PE","2 Pierre":"2PE","1 Jean":"1JN","2 Jean":"2JN","3 Jean":"3JN","Jude":"JUD","Apocalypse":"REV"};
    const code = codes[book]; if (!code) return;
    let url = `https://www.bible.com/fr/bible/63/${code}`;
    if (chapter) { url += `.${chapter}`; if (verse !== "--") url += `.${verse}`; }
    window.open(url, "_blank");
  }

  const availableVerses = useMemo(() => ["--", ...Array.from({ length: 50 }, (_, i) => i + 1)], []);

  return (
    <div className="App" style={{ padding: 16 }}>
      <h1>📚 Étude verset par verset (Rubrique 0)</h1>
      <p style={{ marginTop: -8 }}>Backend: <code>{BACKEND_URL}</code></p>

      <div className="controls-row" style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(7, minmax(120px, 1fr))" }}>
        <Select label="Livre" value={book} options={BOOKS} onChange={(e)=>setBook(e.target.value)} />
        <Select label="Chapitre" value={chapter} options={chapters} onChange={(e)=>setChapter(e.target.value === "--" ? "--" : Number(e.target.value))} />
        <Select label="Verset" value={verse} options={availableVerses} onChange={(e)=>setVerse(e.target.value)} />
        <Select label="Version" value={version} options={["LSG","Darby","NEG"]} onChange={(e)=>setVersion(e.target.value)} />
        <Select label="Longueur" value={targetChars} options={LENGTH_OPTIONS} onChange={(e)=>setTargetChars(Number(e.target.value))} />
        <button className="btn" onClick={openYouVersion}>Lire la Bible</button>
        <button className="btn" onClick={() => { setContent(""); setProgressInfo(null); }}>Reset</button>
      </div>

      <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
        <button className="btn-generate" disabled={loading} onClick={generateFull}>🤖 Générer (Gemini d’abord)</button>
        <button className="btn-versets-prog" disabled={loading} onClick={generateProgressive}>⚡ Versets prog</button>
      </div>

      {progressInfo && (
        <div style={{ marginTop: 10, padding: 8, background: "#eef6ff", borderRadius: 8 }}>
          <strong>Progression :</strong>{" "}
          {progressInfo.current} — {progressInfo.processed}/{progressInfo.total}
        </div>
      )}

      <div className="content-area" style={{ marginTop: 18 }}>
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Génération en cours…</p>
          </div>
        ) : content ? (
          <div className="content-text" dangerouslySetInnerHTML={{ __html: formatHtml(postProcessLabels(content)) }} />
        ) : (
          <div className="welcome-section">
            <h2>Choisis un passage puis clique “Générer”.</h2>
            <p>Astuce : vérifie que <code>/api/health</code> renvoie <code>"gemini": true</code> pour l’enrichissement.</p>
          </div>
        )}
      </div>
    </div>
  );
}

/* =========================
   UI bits
========================= */
function Select({ label, value, options, onChange }) {
  return (
    <div className="select-pill">
      <label style={{ display: "block", fontSize: 12, opacity: 0.8 }}>{label}</label>
      <select value={value} onChange={onChange} style={{ width: "100%" }}>
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}
