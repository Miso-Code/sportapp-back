const { processPayment } = require('../transactions.service');
const { Card } = require('../../models');

jest.mock('../../models', () => ({
  Card: {
    findOne: jest.fn()
  }
}));

describe('Payments Service', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return error if card not found', async () => {
    const cardNumber = '1234567890123456';
    const cardHolder = 'John Doe';
    const cardExpirationDate = '12/25';
    const cardCvv = '123';
    const amount = 100;

    Card.findOne.mockResolvedValueOnce(null);

    const result = await processPayment(
      cardNumber,
      cardHolder,
      cardExpirationDate,
      cardCvv,
      amount
    );

    expect(result)
      .toEqual({
        succeed: false,
        paymentResponse: { error: 'Card not found' }
      });
  });

  it('should return error if card holder is invalid', async () => {
    const cardNumber = '1234567890123456';
    const cardHolder = 'John Doe';
    const cardExpirationDate = '12/25';
    const cardCvv = '123';
    const amount = 100;

    const mockCard = {
      cardHolder: 'Jane Smith'
    };

    Card.findOne.mockResolvedValueOnce(mockCard);

    const result = await processPayment(
      cardNumber,
      cardHolder,
      cardExpirationDate,
      cardCvv,
      amount
    );

    expect(result)
      .toEqual({
        succeed: false,
        paymentResponse: { error: 'Invalid card holder' }
      });
  });

  it('should return error if expiration date is invalid', async () => {
    const cardNumber = '1234567890123456';
    const cardHolder = 'John Doe';
    const cardExpirationDate = '12/20';
    const cardCvv = '123';
    const amount = 100;

    const mockCard = {
      cardHolder,
      cardExpirationDate: '12/25'
    };

    Card.findOne.mockResolvedValueOnce(mockCard);

    const result = await processPayment(
      cardNumber,
      cardHolder,
      cardExpirationDate,
      cardCvv,
      amount
    );

    expect(result)
      .toEqual({
        succeed: false,
        paymentResponse: { error: 'Invalid expiration date' }
      });
  });

  it('should return error if CVV is invalid', async () => {
    const cardNumber = '1234567890123456';
    const cardHolder = 'John Doe';
    const cardExpirationDate = '12/25';
    const cardCvv = '999';
    const amount = 100;

    const mockCard = {
      cardHolder,
      cardExpirationDate,
      cardCvv: '123'
    };

    Card.findOne.mockResolvedValueOnce(mockCard);

    const result = await processPayment(
      cardNumber,
      cardHolder,
      cardExpirationDate,
      cardCvv,
      amount
    );

    expect(result)
      .toEqual({
        succeed: false,
        paymentResponse: { error: 'Invalid CVV' }
      });
  });

  it('should return error if funds are insufficient', async () => {
    const cardNumber = '1234567890123456';
    const cardHolder = 'John Doe';
    const cardExpirationDate = '12/25';
    const cardCvv = '123';
    const amount = 200;

    const mockCard = {
      cardHolder,
      cardExpirationDate,
      cardCvv,
      cardBalance: 100
    };

    Card.findOne.mockResolvedValueOnce(mockCard);

    const result = await processPayment(
      cardNumber,
      cardHolder,
      cardExpirationDate,
      cardCvv,
      amount
    );

    expect(result)
      .toEqual({
        succeed: false,
        paymentResponse: { error: 'Insufficient funds' }
      });
  });

  it('should process payment successfully', async () => {
    const cardNumber = '1234567890123456';
    const cardHolder = 'John Doe';
    const cardExpirationDate = '12/25';
    const cardCvv = '123';
    const amount = 50;

    const mockCard = {
      cardHolder,
      cardExpirationDate,
      cardCvv,
      cardBalance: 100,
      decrement: jest.fn()
    };

    Card.findOne.mockResolvedValueOnce(mockCard);

    const result = await processPayment(
      cardNumber,
      cardHolder,
      cardExpirationDate,
      cardCvv,
      amount
    );

    expect(result)
      .toEqual({
        succeed: true,
        paymentResponse: { message: 'Payment processed successfully' }
      });
  });
});
