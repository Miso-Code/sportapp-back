const crypto = require('crypto');
const { SubscriptionTypeEnum } = require('../models/enums');

function getUserScopes(userSubscriptionType) {
  const scopes = ['free'];
  // eslint-disable-next-line default-case
  switch (userSubscriptionType) {
    case SubscriptionTypeEnum.INTERMEDIATE:
      scopes.push('intermediate');
      break;
    case SubscriptionTypeEnum.PREMIUM:
      scopes.push('intermediate');
      scopes.push('premium');
  }

  return scopes;
}

function hashPassword(password) {
  return crypto.createHash('sha256').update(password).digest('hex');
}

function comparePassword(providedPassword, storedHash) {
  const providedHash = hashPassword(providedPassword);
  return storedHash === providedHash;
}

module.exports = {
  getUserScopes, hashPassword, comparePassword
};
