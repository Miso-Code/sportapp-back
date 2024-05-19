const { comparePassword, hashPassword } = require('../../utils');
const User = require('../../models/user.model');
const { decodeRefreshToken, generateTokens } = require('../../security/jwt');
const { registerUser, loginUser } = require('../user.service');

jest.mock('../../utils');
jest.mock('../../models/user.model');
jest.mock('../../security/jwt');

describe('User Service', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('registerUser', () => {
    it('should register a new user successfully', async () => {
      const user = {
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        password: 'password123'
      };
      const hashedPassword = 'hashedPassword';
      const newUser = {
        user_id: '123',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com'
      };

      User.findOne.mockResolvedValue(null);
      hashPassword.mockResolvedValue(hashedPassword);
      User.create.mockResolvedValue({ ...newUser, hashed_password: hashedPassword });

      const result = await registerUser(user);

      expect(User.findOne).toHaveBeenCalledWith({ where: { email: user.email } });
      expect(hashPassword).toHaveBeenCalledWith(user.password);
      expect(User.create).toHaveBeenCalledWith({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
        hashed_password: hashedPassword
      });
      expect(result).toEqual(newUser);
    });

    it('should throw an error if the user already exists', async () => {
      const user = {
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        password: 'password123'
      };

      User.findOne.mockResolvedValue({});

      await expect(registerUser(user)).rejects.toThrow('User already exists');
    });
  });

  describe('loginUser', () => {
    it('should login a user with correct password', async () => {
      const userLoginData = {
        email: 'john.doe@example.com',
        password: 'password123'
      };
      const existingUser = {
        user_id: '123',
        email: 'john.doe@example.com',
        hashed_password: 'hashedPassword',
        subscription_type: 'premium'
      };
      const tokens = {
        access_token: 'accessToken',
        refresh_token: 'refreshToken'
      };

      User.findOne.mockResolvedValue(existingUser);
      comparePassword.mockResolvedValue(true);
      generateTokens.mockReturnValue(tokens);

      const result = await loginUser(userLoginData);

      expect(User.findOne).toHaveBeenCalledWith({ where: { email: userLoginData.email } });
      expect(comparePassword)
        .toHaveBeenCalledWith(userLoginData.password, existingUser.hashed_password);
      expect(generateTokens)
        .toHaveBeenCalledWith(existingUser.user_id, existingUser.subscription_type);
      expect(result).toEqual(tokens);
    });

    it('should throw an error if the user does not exist', async () => {
      const userLoginData = {
        email: 'john.doe@example.com',
        password: 'password123'
      };

      User.findOne.mockResolvedValue(null);

      await expect(loginUser(userLoginData)).rejects.toThrow('User does not exist');
    });

    it('should throw an error if the password is incorrect', async () => {
      const userLoginData = {
        email: 'john.doe@example.com',
        password: 'password123'
      };
      const existingUser = {
        user_id: '123',
        email: 'john.doe@example.com',
        hashed_password: 'hashedPassword'
      };

      User.findOne.mockResolvedValue(existingUser);
      comparePassword.mockResolvedValue(false);

      await expect(loginUser(userLoginData)).rejects.toThrow('Invalid password');
    });

    it('should generate new tokens with a valid refresh token', async () => {
      const userLoginData = {
        refreshToken: 'validRefreshToken'
      };
      const existingUser = {
        user_id: '123',
        subscription_type: 'premium'
      };
      const tokens = {
        access_token: 'accessToken',
        refresh_token: 'refreshToken'
      };

      User.findOne.mockResolvedValue(existingUser);
      decodeRefreshToken.mockReturnValue(existingUser.user_id);
      generateTokens.mockReturnValue(tokens);

      const result = await loginUser(userLoginData);

      expect(decodeRefreshToken).toHaveBeenCalledWith(userLoginData.refreshToken);
      expect(generateTokens)
        .toHaveBeenCalledWith(existingUser.user_id, existingUser.subscription_type);
      expect(result).toEqual(tokens);
    });

    it('should throw an error with an invalid or expired refresh token', async () => {
      const userLoginData = {
        refreshToken: 'invalidRefreshToken'
      };

      decodeRefreshToken.mockImplementation(() => {
        throw new Error('Invalid or expired refresh token');
      });

      await expect(loginUser(userLoginData)).rejects.toThrow('Invalid or expired refresh token');
    });
  });
});
