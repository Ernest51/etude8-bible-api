const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxies pour les endpoints spécifiques du backend local
  app.use(
    '/api/generate-verse-by-verse',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
    })
  );

  app.use(
    '/api/generate-verse-by-verse-gemini',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
    })
  );

  app.use(
    '/api/generate-study',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
    })
  );

  app.use(
    '/api/books',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
    })
  );

  app.use(
    '/api/meditations',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
    })
  );

  // Proxies pour external API fallbacks
  app.use(
    '/api/verse-proxy',
    createProxyMiddleware({
      target: 'https://etude8-bible-api-production.up.railway.app',
      changeOrigin: true,
      pathRewrite: {
        '^/api/verse-proxy': '/api',
      },
    })
  );

  app.use(
    '/api/study-proxy',
    createProxyMiddleware({
      target: 'https://etude28-bible-api-production.up.railway.app',
      changeOrigin: true,
      pathRewrite: {
        '^/api/study-proxy': '/api',
      },
    })
  );
};