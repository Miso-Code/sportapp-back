const jwt = require('jsonwebtoken');
const { getUserScopes } = require('../../utils');
const Config = require('../../config');
const { generateTokens, decodeRefreshToken } = require('../jwt');

jest.mock('jsonwebtoken');
jest.mock('../../utils');
jest.mock('../../config');

describe('JWT Functions', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('generateTokens', () => {
    it('should generate access and refresh tokens with correct payload', () => {
      const userId = 'testUser';
      const userSubscriptionType = 'premium';
      const scopes = ['read', 'write'];

      getUserScopes.mockReturnValue(scopes);
      jwt.sign.mockReturnValue('fakeToken');

      const result = generateTokens(userId, userSubscriptionType);

      expect(result.user_id).toBe(userId);
      expect(result.access_token).toBe('fakeToken');
      expect(result.refresh_token).toBe('fakeToken');
      expect(result.access_token_expires_minutes).toBe(Config.ACCESS_TOKEN_EXPIRE_MINUTES);
      expect(result.refresh_token_expires_minutes).toBe(Config.REFRESH_TOKEN_EXPIRE_MINUTES);

      const expectedPayload = { user_id: userId, scopes };
      expect(jwt.sign).toHaveBeenCalledWith(
        { ...expectedPayload, expiry: expect.any(Number) },
        Config.JWT_SECRET_KEY,
        { algorithm: Config.JWT_ALGORITHM }
      );
    });
  });

  describe('decodeRefreshToken', () => {
    it('should decode a valid refresh token and return userId', () => {
      const refreshToken = 'validRefreshToken';
      const decodedPayload = {
        userId: 'testUser',
        expiry: Math.floor(Date.now() / 1000) + 60 * 60,
        refresh: true
      };

      jwt.verify.mockReturnValue(decodedPayload);

      const userId = decodeRefreshToken(refreshToken);

      expect(userId).toBe(decodedPayload.userId);
      expect(jwt.verify).toHaveBeenCalledWith(
        refreshToken,
        Config.JWT_SECRET_KEY,
        { algorithms: [Config.JWT_ALGORITHM] }
      );
    });

    it('should throw an error if the token is invalid', () => {
      const refreshToken = 'invalidToken';

      jwt.verify.mockImplementation(() => {
        throw new Error('invalid token');
      });

      expect(() => decodeRefreshToken(refreshToken)).toThrow('Invalid or expired refresh token');
    });

    it('should throw an error if the token is not a refresh token', () => {
      const refreshToken = 'notRefreshToken';
      const decodedPayload = {
        userId: 'testUser',
        expiry: Math.floor(Date.now() / 1000) + 60 * 60,
        refresh: false
      };

      jwt.verify.mockReturnValue(decodedPayload);

      expect(() => decodeRefreshToken(refreshToken)).toThrow('Not a refresh token');
    });

    it('should throw an error if the token is expired', () => {
      const refreshToken = 'expiredToken';
      const decodedPayload = {
        userId: 'testUser',
        expiry: Math.floor(Date.now() / 1000) - 60,
        refresh: true
      };

      jwt.verify.mockReturnValue(decodedPayload);

      expect(() => decodeRefreshToken(refreshToken)).toThrow('Invalid or expired refresh token');
    });
  });
});
