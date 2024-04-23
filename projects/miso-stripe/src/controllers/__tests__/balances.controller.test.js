const {
  HTTP_STATUS_OK,
  HTTP_STATUS_INTERNAL_SERVER_ERROR,
  HTTP_STATUS_BAD_REQUEST
} = require('http2').constants;

const {
  addBalanceToCard,
  removeBalanceToCard
} = require('../balances.controller');

const balancesService = require('../../services/balances.service');
const { balanceSchema } = require('../../models/schemas/balance.schema');

// Mock balanceSchema
jest.mock('../../models/schemas/balance.schema', () => ({
  balanceSchema: {
    validate: jest.fn()
  }
}));

// Mock balancesService
jest.mock('../../services/balances.service', () => ({
  deposit: jest.fn(),
  withdraw: jest.fn()
}));

describe('addBalanceToCard', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return HTTP_STATUS_BAD_REQUEST if validation fails', async () => {
    const req = { body: {} };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    const error = new Error('Validation error');
    balanceSchema.validate.mockReturnValueOnce({ error });

    await addBalanceToCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json)
      .toHaveBeenCalledWith({ error: error.message });
  });

  it('should return HTTP_STATUS_INTERNAL_SERVER_ERROR if an error occurs during deposit', async () => {
    const req = {
      body: {
        amount: 100,
        cardNumber: '1234'
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    balanceSchema.validate.mockReturnValueOnce({ value: req.body });
    balancesService.deposit.mockRejectedValueOnce(new Error('Deposit error'));

    await addBalanceToCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_INTERNAL_SERVER_ERROR);
    expect(res.json)
      .toHaveBeenCalledWith({ error: 'Deposit error' });
  });

  it('should return HTTP_STATUS_BAD_REQUEST if deposit does not succeed', async () => {
    const req = {
      body: {
        amount: 100,
        cardNumber: '1234'
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    balanceSchema.validate.mockReturnValueOnce({ value: req.body });
    balancesService.deposit.mockResolvedValueOnce({
      succeed: false,
      depositResponse: { error: 'Deposit failed' }
    });

    await addBalanceToCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json)
      .toHaveBeenCalledWith({ error: 'Deposit failed' });
  });

  it('should return HTTP_STATUS_OK and depositResponse if deposit succeeds', async () => {
    const req = {
      body: {
        amount: 100,
        cardNumber: '1234'
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    balanceSchema.validate.mockReturnValueOnce({ value: req.body });
    balancesService.deposit.mockResolvedValueOnce({
      succeed: true,
      depositResponse: { message: 'Deposit successful' }
    });

    await addBalanceToCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_OK);
    expect(res.json)
      .toHaveBeenCalledWith({ message: 'Deposit successful' });
  });
});

describe('removeBalanceToCard', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return HTTP_STATUS_BAD_REQUEST if validation fails', async () => {
    const req = { body: {} };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    const error = new Error('Validation error');
    balanceSchema.validate.mockReturnValueOnce({ error });

    await removeBalanceToCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json)
      .toHaveBeenCalledWith({ error: error.message });
  });

  it('should return HTTP_STATUS_INTERNAL_SERVER_ERROR if an error occurs during withdraw', async () => {
    const req = {
      body: {
        amount: 100,
        cardNumber: '1234'
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    balanceSchema.validate.mockReturnValueOnce({ value: req.body });
    balancesService.withdraw.mockRejectedValueOnce(new Error('Withdraw error'));

    await removeBalanceToCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_INTERNAL_SERVER_ERROR);
    expect(res.json)
      .toHaveBeenCalledWith({ error: 'Withdraw error' });
  });

  it('should return HTTP_STATUS_BAD_REQUEST if withdraw does not succeed', async () => {
    const req = {
      body: {
        amount: 100,
        cardNumber: '1234'
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    balanceSchema.validate.mockReturnValueOnce({ value: req.body });
    balancesService.withdraw.mockResolvedValueOnce({
      succeed: false,
      withdrawResponse: { error: 'Withdraw failed' }
    });

    await removeBalanceToCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json)
      .toHaveBeenCalledWith({ error: 'Withdraw failed' });
  });

  it('should return HTTP_STATUS_OK and withdrawResponse if withdraw succeeds', async () => {
    const req = {
      body: {
        amount: 100,
        cardNumber: '1234'
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    balanceSchema.validate.mockReturnValueOnce({ value: req.body });
    balancesService.withdraw.mockResolvedValueOnce({
      succeed: true,
      withdrawResponse: { message: 'Withdraw successful' }
    });

    await removeBalanceToCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_OK);
    expect(res.json)
      .toHaveBeenCalledWith({ message: 'Withdraw successful' });
  });
});
