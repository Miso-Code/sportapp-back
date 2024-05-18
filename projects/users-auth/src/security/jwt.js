const jwt = require('jsonwebtoken');
const { getUserScopes } = require('../utils');
const Config = require('../config');

const INVALID_EXPIRED_MESSAGE = 'Invalid or expired refresh token';

function createToken(payload, expiresInMinutes, refresh = false) {
  const newPayload = { ...payload };
  if (refresh) {
    newPayload.refresh = true;
  }
  const expirationTime = Math.floor(Date.now() / 1000) + (expiresInMinutes * 60);
  const payloadWithExp = { ...newPayload, expiry: expirationTime };
  return jwt.sign(payloadWithExp, Config.JWT_SECRET_KEY, { algorithm: Config.JWT_ALGORITHM });
}

function decodeToken(token) {
  return jwt.verify(token, Config.JWT_SECRET_KEY, { algorithms: [Config.JWT_ALGORITHM] });
}

function generateTokens(userId, userSubscriptionType) {
  const scopes = getUserScopes(userSubscriptionType);
  const payload = { user_id: userId, scopes };
  return {
    user_id: userId,
    access_token: createToken(payload, Config.ACCESS_TOKEN_EXPIRE_MINUTES),
    access_token_expires_minutes: Config.ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_token: createToken(payload, Config.REFRESH_TOKEN_EXPIRE_MINUTES, true),
    refresh_token_expires_minutes: Config.REFRESH_TOKEN_EXPIRE_MINUTES
  };
}

function decodeRefreshToken(refreshToken) {
  let payload;
  try {
    payload = decodeToken(refreshToken);
  }
  catch (err) {
    throw new Error(INVALID_EXPIRED_MESSAGE);
  }
  if (!payload || !payload.expiry) {
    throw new Error(INVALID_EXPIRED_MESSAGE);
  }
  if (!payload.refresh) {
    throw new Error('Not a refresh token');
  }
  if (Date.now() / 1000 > payload.expiry) {
    throw new Error(INVALID_EXPIRED_MESSAGE);
  }

  return payload.userId;
}

module.exports = {
  generateTokens,
  decodeRefreshToken
};
