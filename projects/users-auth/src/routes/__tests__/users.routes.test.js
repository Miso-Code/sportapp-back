const { Router } = require('express');
const usersRouter = require('../users.routes');
const usersController = require('../../controllers/users.controller');

jest.mock('../../controllers/users.controller', () => ({
  register: jest.fn(),
  login: jest.fn()
}));

describe('Users Router', () => {
  let router;

  beforeEach(() => {
    router = Router();
    router.use('/', usersRouter);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should call register controller when POST /register is called', () => {
    const req = {
      method: 'POST',
      url: '/register'
    };
    const res = {};
    const next = jest.fn();

    router.handle(req, res, next);

    expect(usersController.register)
      .toHaveBeenCalledWith(req, res, expect.any(Function));
  });

  it('should call login controller when POST /login is called', () => {
    const req = {
      method: 'POST',
      url: '/login'
    };
    const res = {};
    const next = jest.fn();

    router.handle(req, res, next);

    expect(usersController.login)
      .toHaveBeenCalledWith(req, res, expect.any(Function));
  });
});
