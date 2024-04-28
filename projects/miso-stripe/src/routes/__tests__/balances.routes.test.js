const { Router } = require('express');
const balancesRouter = require('../balances.routes');
const balancesController = require('../../controllers/balances.controller');

jest.mock('../../controllers/balances.controller', () => ({
  addBalanceToCard: jest.fn(),
  removeBalanceToCard: jest.fn()
}));

describe('Balances Router', () => {
  let router;

  beforeEach(() => {
    router = Router();
    router.use('/balances', balancesRouter);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should call addBalanceToCard controller when POST /balances/add is called', () => {
    const req = {
      body: {
        amount: 100,
        cardNumber: '1234567890123456'
      },
      method: 'POST',
      url: '/balances/add'
    };
    const res = {};
    const next = jest.fn();

    router.handle(req, res, next);

    expect(balancesController.addBalanceToCard)
      .toHaveBeenCalledWith(req, res, expect.any(Function));
  });

  it('should call removeBalanceToCard controller when POST /balances/remove is called', () => {
    const req = {
      body: {
        amount: 100,
        cardNumber: '1234567890123456'
      },
      method: 'POST',
      url: '/balances/remove'
    };
    const res = {};
    const next = jest.fn();

    router.handle(req, res, next);

    expect(balancesController.removeBalanceToCard)
      .toHaveBeenCalledWith(req, res, expect.any(Function));
  });
});
