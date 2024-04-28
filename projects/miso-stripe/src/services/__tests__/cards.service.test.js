const {
  createCard,
  getCards
} = require('../cards.service');
const { Card } = require('../../models');

jest.mock('../../models', () => ({
  Card: {
    create: jest.fn(),
    findAll: jest.fn(),
    findOne: jest.fn()
  }
}));

describe('Cards Service', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('createCard', () => {
    it('should create a new card with valid expiration date', async () => {
      const cardNumber = '1234567890123456';
      const cardHolder = 'John Doe';
      const cardExpirationDate = '12/25';
      const cardCvv = '123';
      const cardBalance = 100;

      Card.create.mockResolvedValueOnce({
        cardNumber,
        cardHolder,
        cardExpirationDate,
        cardCvv,
        cardBalance
      });

      const result = await createCard(
        cardNumber,
        cardHolder,
        cardExpirationDate,
        cardCvv,
        cardBalance
      );

      expect(Card.create)
        .toHaveBeenCalledWith({
          cardNumber,
          cardHolder,
          cardExpirationDate,
          cardCvv,
          cardBalance
        });
      expect(result.card)
        .toBeTruthy();
      expect(result.createError)
        .toBeNull();
    });

    it('should return null card and createError message if card exists', async () => {
      const cardNumber = '1234567890123456';
      const cardHolder = 'John Doe';
      const cardExpirationDate = '12/25';
      const cardCvv = '123';
      const cardBalance = 100;

      Card.findOne.mockResolvedValueOnce({
        cardNumber,
        cardHolder,
        cardExpirationDate,
        cardCvv,
        cardBalance
      });

      const result = await createCard(
        cardNumber,
        cardHolder,
        cardExpirationDate,
        cardCvv,
        cardBalance
      );

      expect(Card.findOne)
        .toHaveBeenCalled();

      expect(result.card)
        .toBeNull();

      expect(result.createError)
        .toEqual({ message: 'Card already exists' });
    });

    it('should return null card and createError message if card has expired', async () => {
      const cardNumber = '1234567890123456';
      const cardHolder = 'John Doe';
      const cardExpirationDate = '12/20';
      const cardCvv = '123';
      const cardBalance = 100;

      const result = await createCard(
        cardNumber,
        cardHolder,
        cardExpirationDate,
        cardCvv,
        cardBalance
      );

      expect(result.card)
        .toBeNull();
      expect(result.createError)
        .toEqual({ message: 'Card has expired' });
    });
  });

  describe('getCards', () => {
    it('should return all cards', async () => {
      const mockCards = [
        {
          cardNumber: '1234567890123456',
          cardHolder: 'John Doe',
          cardBalance: 100
        },
        {
          cardNumber: '9876543210987654',
          cardHolder: 'Jane Smith',
          cardBalance: 200
        }
      ];
      Card.findAll.mockResolvedValueOnce(mockCards);

      const result = await getCards();

      expect(Card.findAll)
        .toHaveBeenCalled();
      expect(result)
        .toEqual(mockCards);
    });
  });
});
