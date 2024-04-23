const {
  HTTP_STATUS_UNAUTHORIZED
} = require('http2').constants;

const authMiddleware = async (req, res, next) => {
  if (req.path !== '/ping') {
    const apiKey = process.env.API_KEY;
    const requestApiKey = req.get('api_key');
    if (apiKey !== requestApiKey) {
      return res.status(HTTP_STATUS_UNAUTHORIZED)
        .send('Not authenticated');
    }
  }

  return next();
};

module.exports = authMiddleware;
