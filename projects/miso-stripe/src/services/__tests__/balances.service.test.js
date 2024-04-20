const {
  deposit,
  withdraw
} = require('../balances.service');
const { Card } = require('../../models');

jest.mock('../../models', () => ({
  Card: {
    findOne: jest.fn(),
    increment: jest.fn(),
    decrement: jest.fn()
  }
}));

describe('Balances Service', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('deposit', () => {
    it('should deposit amount to card balance and return success message', async () => {
      const mockCard = {
        cardNumber: '1234567890123456',
        cardBalance: 0,
        increment: jest.fn()
      };
      Card.findOne.mockResolvedValueOnce(mockCard);
      const amount = 100;

      const result = await deposit('1234567890123456', amount);

      expect(Card.findOne)
        .toHaveBeenCalledWith({ where: { cardNumber: '1234567890123456' } });
      expect(mockCard.increment)
        .toHaveBeenCalledWith('cardBalance', { by: amount });
      expect(result)
        .toEqual({
          succeed: true,
          depositResponse: { message: `Deposit of $${amount} for card 1234567890123456 succeed` }
        });
    });

    it('should return error if card not found', async () => {
      Card.findOne.mockResolvedValueOnce(null);
      const amount = 100;

      const result = await deposit('1234567890123456', amount);

      expect(result)
        .toEqual({
          succeed: false,
          depositResponse: { error: 'Card not found' }
        });
    });
  });

  describe('withdraw', () => {
    it('should withdraw amount from card balance and return success message', async () => {
      const mockCard = {
        cardNumber: '1234567890123456',
        cardBalance: 200,
        decrement: jest.fn()
      };
      Card.findOne.mockResolvedValueOnce(mockCard);
      const amount = 100;

      const result = await withdraw('1234567890123456', amount);

      expect(Card.findOne)
        .toHaveBeenCalledWith({ where: { cardNumber: '1234567890123456' } });
      expect(mockCard.decrement)
        .toHaveBeenCalledWith('cardBalance', { by: amount });
      expect(result)
        .toEqual({
          succeed: true,
          withdrawResponse: { message: `Withdraw of $${amount} for card 1234567890123456 succeed` }
        });
    });

    it('should return error if card not found', async () => {
      Card.findOne.mockResolvedValueOnce(null);
      const amount = 100;

      const result = await withdraw('1234567890123456', amount);

      expect(result)
        .toEqual({
          succeed: false,
          withdrawResponse: { error: 'Card not found' }
        });
    });

    it('should return error if card balance is insufficient', async () => {
      const mockCard = {
        cardNumber: '1234567890123456',
        cardBalance: 50
      };
      Card.findOne.mockResolvedValueOnce(mockCard);
      const amount = 100;

      const result = await withdraw('1234567890123456', amount);

      expect(result)
        .toEqual({
          succeed: false,
          withdrawResponse: { error: 'Insufficient funds' }
        });
    });
  });
});
