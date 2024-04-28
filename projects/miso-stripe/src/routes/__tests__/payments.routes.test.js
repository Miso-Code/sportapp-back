const { Router } = require('express');
const paymentsRouter = require('../payments.routes');
const paymentsController = require('../../controllers/payments.controller');

jest.mock('../../controllers/payments.controller', () => ({
  cardPayment: jest.fn()
}));

describe('Payments Router', () => {
  let router;

  beforeEach(() => {
    router = Router();
    router.use('/payments', paymentsRouter);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should call cardPayment controller when POST /payments is called', () => {
    const req = {
      method: 'POST',
      url: '/payments'
    };
    const res = {};
    const next = jest.fn();

    router.handle(req, res, next);

    expect(paymentsController.cardPayment)
      .toHaveBeenCalledWith(req, res, expect.any(Function));
  });
});
