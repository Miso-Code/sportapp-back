const { Router } = require('express');
const cardsRouter = require('../cards.routes');
const cardsController = require('../../controllers/cards.controller');

jest.mock('../../controllers/cards.controller', () => ({
  getCards: jest.fn(),
  createCard: jest.fn()
}));

describe('Cards Router', () => {
  let router;

  beforeEach(() => {
    router = Router();
    router.use('/cards', cardsRouter);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should call getCards controller when GET /cards is called', () => {
    const req = {
      method: 'GET',
      url: '/cards'
    };
    const res = {};
    const next = jest.fn();

    router.handle(req, res, next);

    expect(cardsController.getCards)
      .toHaveBeenCalledWith(req, res, expect.any(Function));
  });

  it('should call createCard controller when POST /cards is called', () => {
    const req = {
      method: 'POST',
      url: '/cards'
    };
    const res = {};
    const next = jest.fn();

    router.handle(req, res, next);

    expect(cardsController.createCard)
      .toHaveBeenCalledWith(req, res, expect.any(Function));
  });
});
