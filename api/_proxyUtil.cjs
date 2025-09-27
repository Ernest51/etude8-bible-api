async function proxyPass(req, res, targetPath) {
  try {
    const base = process.env.API_TARGET_BASE;
    if (!base) return res.status(500).json({ error: "API_TARGET_BASE non configuré" });

    const url = `${base}${targetPath}`;
    const headers = { ...req.headers };
    delete headers.host;

    const init = { method: req.method, headers };
    if (req.method !== "GET" && req.method !== "HEAD") {
      init.headers["content-type"] = "application/json";
      init.body = JSON.stringify(req.body || {});
    }

    const r = await fetch(url, init);
    const text = await r.text();
    const ct = r.headers.get("content-type") || "";
    res.status(r.status);
    if (ct) res.setHeader("content-type", ct);
    res.send(text);
  } catch (e) {
    res.status(502).json({ error: "ProxyError", message: e?.message || String(e) });
  }
}
module.exports = { proxyPass };
