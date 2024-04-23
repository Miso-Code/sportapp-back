const {
  HTTP_STATUS_OK,
  HTTP_STATUS_CREATED,
  HTTP_STATUS_INTERNAL_SERVER_ERROR,
  HTTP_STATUS_BAD_REQUEST
} = require('http2').constants;

const {
  getCards,
  createCard
} = require('../cards.controller');

const cardsService = require('../../services/cards.service');
const { cardSchema } = require('../../models/schemas/card.schema');

// Mock cardSchema
jest.mock('../../models/schemas/card.schema', () => ({
  cardSchema: {
    validate: jest.fn()
  }
}));

// Mock cardsService
jest.mock('../../services/cards.service', () => ({
  getCards: jest.fn(),
  createCard: jest.fn()
}));

describe('getCards', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should return HTTP_STATUS_OK with cards data', async () => {
    const cardsData = [{
      cardNumber: '1234567890123456',
      cardHolder: 'John Doe'
    }];
    cardsService.getCards.mockResolvedValueOnce(cardsData);
    const req = {};
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };

    await getCards(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_OK);
    expect(res.json)
      .toHaveBeenCalledWith(cardsData);
  });

  it('should return HTTP_STATUS_INTERNAL_SERVER_ERROR if an error occurs', async () => {
    const error = new Error('Internal server error');
    cardsService.getCards.mockRejectedValueOnce(error);
    const req = {};
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };

    await getCards(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_INTERNAL_SERVER_ERROR);
    expect(res.json)
      .toHaveBeenCalledWith({ error: error.message });
  });
});

describe('createCard', () => {
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
    cardSchema.validate.mockReturnValueOnce({ error });

    await createCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json)
      .toHaveBeenCalledWith({ error: error.message });
  });

  it('should return HTTP_STATUS_BAD_REQUEST if creation fails for business logic', async () => {
    const req = { body: {} };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    const mockResult = {
      card: null,
      createError: {
        message: 'Business logic error'
      }
    };

    cardSchema.validate.mockReturnValueOnce({ value: req.body });
    cardsService.createCard.mockResolvedValueOnce(mockResult);

    await createCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_BAD_REQUEST);
    expect(res.json)
      .toHaveBeenCalledWith(mockResult.createError);
  });

  it('should return HTTP_STATUS_INTERNAL_SERVER_ERROR if an error occurs during card creation', async () => {
    const req = {
      body: {
        cardNumber: '1234567890123456',
        cardHolder: 'John Doe',
        cardExpirationDate: '01/25',
        cardCvv: '123'
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    cardSchema.validate.mockReturnValueOnce({ value: req.body });
    const error = new Error('Internal server error');
    cardsService.createCard.mockRejectedValueOnce(error);

    await createCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_INTERNAL_SERVER_ERROR);
    expect(res.json)
      .toHaveBeenCalledWith({ error: error.message });
  });

  it('should return HTTP_STATUS_CREATED and card data if card creation succeeds', async () => {
    const req = {
      body: {
        cardNumber: '1234567890123456',
        cardHolder: 'John Doe',
        cardExpirationDate: '01/25',
        cardCvv: '123'
      }
    };
    const res = {
      status: jest.fn()
        .mockReturnThis(),
      json: jest.fn()
    };
    const cardData = {
      cardNumber: '1234567890123456',
      cardHolder: 'John Doe',
      cardExpirationDate: '01/25',
      cardCvv: '123'
    };
    const mockResult = {
      card: cardData,
      createError: null
    };
    cardSchema.validate.mockReturnValueOnce({ value: req.body });
    cardsService.createCard.mockResolvedValueOnce(mockResult);

    await createCard(req, res);

    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_CREATED);
    expect(res.json)
      .toHaveBeenCalledWith(cardData);
  });
});
