const {
  HTTP_STATUS_OK,
  HTTP_STATUS_INTERNAL_SERVER_ERROR,
  HTTP_STATUS_BAD_REQUEST
} = require('http2').constants;

const { cardPayment } = require('../payments.controller');

const transactionsService = require('../../services/transactions.service');
const { transactionSchema } = require('../../models/schemas/transaction.schema');

// Mock transactionSchema
jest.mock('../../models/schemas/transaction.schema', () => ({
  transactionSchema: {
    validate: jest.fn()
  }
}));

// Mock transactionsService
jest.mock('../../services/transactions.service', () => ({
  processPayment: jest.fn()
}));

describe('cardPayment', () => {
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
    transactionSchema.validate.mockReturnValueOnce({ error });

    await cardPayment(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json)
      .toHaveBeenCalledWith({ error: error.message });
  });

  it('should return HTTP_STATUS_INTERNAL_SERVER_ERROR if an error occurs during payment processing', async () => {
    const req = {
      body: {
        cardNumber: '1234567890123456',
        cardHolder: 'John Doe',
        cardExpirationDate: '01/25',
        cardCvv: '123',
        amount: 100
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    transactionSchema.validate.mockReturnValueOnce({ value: req.body });
    const error = new Error('Internal server error');
    transactionsService.processPayment.mockRejectedValueOnce(error);

    await cardPayment(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_INTERNAL_SERVER_ERROR);
    expect(res.json)
      .toHaveBeenCalledWith({ error: error.message });
  });

  it('should return HTTP_STATUS_BAD_REQUEST if payment does not succeed', async () => {
    const req = {
      body: {
        cardNumber: '1234567890123456',
        cardHolder: 'John Doe',
        cardExpirationDate: '01/25',
        cardCvv: '123',
        amount: 100
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    transactionSchema.validate.mockReturnValueOnce({ value: req.body });
    transactionsService.processPayment.mockResolvedValueOnce({
      succeed: false,
      paymentResponse: { error: 'Payment failed' }
    });

    await cardPayment(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json)
      .toHaveBeenCalledWith({ error: 'Payment failed' });
  });

  it('should return HTTP_STATUS_OK and paymentResponse if payment succeeds', async () => {
    const req = {
      body: {
        cardNumber: '1234567890123456',
        cardHolder: 'John Doe',
        cardExpirationDate: '01/25',
        cardCvv: '123',
        amount: 100
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    const paymentResponse = { message: 'Payment successful' };
    transactionSchema.validate.mockReturnValueOnce({ value: req.body });
    transactionsService.processPayment.mockResolvedValueOnce({
      succeed: true,
      paymentResponse
    });

    await cardPayment(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_OK);
    expect(res.json)
      .toHaveBeenCalledWith(paymentResponse);
  });
});
