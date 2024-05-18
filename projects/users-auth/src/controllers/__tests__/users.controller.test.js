const {
  HTTP_STATUS_OK,
  HTTP_STATUS_CREATED,
  HTTP_STATUS_BAD_REQUEST
} = require('http2').constants;

const {
  register,
  login
} = require('../users.controller');

const usersService = require('../../services/user.service');
const { userSchema, loginSchema } = require('../../models/schemas');

jest.mock('../../models/schemas', () => ({
  userSchema: {
    validate: jest.fn()
  },
  loginSchema: {
    validate: jest.fn()
  }
}));

// Mock usersService
jest.mock('../../services/user.service', () => ({
  registerUser: jest.fn(),
  loginUser: jest.fn()
}));

describe('register', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return HTTP_STATUS_BAD_REQUEST if validation fails', async () => {
    const req = { body: {} };
    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    const error = new Error('Validation error');
    userSchema.validate.mockReturnValueOnce({ error });

    await register(req, res);

    expect(res.status).toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json).toHaveBeenCalledWith({ error: error.message });
  });

  it('should return HTTP_STATUS_CREATED and user data if registration succeeds', async () => {
    const req = { body: { username: 'testuser', password: 'password123' } };
    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    const userData = { id: 1, username: 'testuser' };
    userSchema.validate.mockReturnValueOnce({ value: req.body });
    usersService.registerUser.mockResolvedValueOnce(userData);

    await register(req, res);

    expect(res.status).toHaveBeenCalledWith(HTTP_STATUS_CREATED);
    expect(res.json).toHaveBeenCalledWith(userData);
  });

  it('should return HTTP_STATUS_BAD_REQUEST if registration fails', async () => {
    const req = { body: { username: 'testuser', password: 'password123' } };
    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    const error = new Error('Registration error');
    userSchema.validate.mockReturnValueOnce({ value: req.body });
    usersService.registerUser.mockRejectedValueOnce(error);

    await register(req, res);

    expect(res.status).toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json).toHaveBeenCalledWith({ error: error.message });
  });
});

describe('login', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return HTTP_STATUS_BAD_REQUEST if validation fails', async () => {
    const req = { body: {} };
    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    const error = new Error('Validation error');
    loginSchema.validate.mockReturnValueOnce({ error });

    await login(req, res);

    expect(res.status).toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json).toHaveBeenCalledWith({ error: error.message });
  });

  it('should return HTTP_STATUS_OK and user data if login succeeds', async () => {
    const req = { body: { username: 'testuser', password: 'password123' } };
    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    const userData = { id: 1, username: 'testuser' };
    loginSchema.validate.mockReturnValueOnce({ value: req.body });
    usersService.loginUser.mockResolvedValueOnce(userData);

    await login(req, res);

    expect(res.status).toHaveBeenCalledWith(HTTP_STATUS_OK);
    expect(res.json).toHaveBeenCalledWith(userData);
  });

  it('should return HTTP_STATUS_BAD_REQUEST if login fails', async () => {
    const req = { body: { username: 'testuser', password: 'password123' } };
    const res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    const error = new Error('Login error');
    loginSchema.validate.mockReturnValueOnce({ value: req.body });
    usersService.loginUser.mockRejectedValueOnce(error);

    await login(req, res);

    expect(res.status).toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json).toHaveBeenCalledWith({ error: error.message });
  });
});
