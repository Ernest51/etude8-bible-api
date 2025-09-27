const { proxyPass } = require("./_proxyUtil.cjs");
module.exports = (req, res) =>
  proxyPass(req, res, "/api/generate-verse-by-verse-progressive");
