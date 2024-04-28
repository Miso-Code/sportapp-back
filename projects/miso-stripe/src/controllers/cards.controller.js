const {
  HTTP_STATUS_OK,
  HTTP_STATUS_CREATED,
  HTTP_STATUS_INTERNAL_SERVER_ERROR,
  HTTP_STATUS_BAD_REQUEST
} = require('http2').constants;

const { cardSchema } = require('../models/schemas/card.schema');
const cardsService = require('../services/cards.service');

const getCards = async (req, res) => {
  try {
    const cards = await cardsService.getCards();
    res.status(HTTP_STATUS_OK).json(cards);
  }
  catch (error) {
    res.status(HTTP_STATUS_INTERNAL_SERVER_ERROR).json({ error: error.message });
  }
};

const createCard = async (req, res) => {
  const { error, value } = cardSchema.validate(req.body);

  if (error) {
    return res.status(HTTP_STATUS_BAD_REQUEST).json({ error: error.message });
  }

  const {
    cardNumber, cardHolder, cardExpirationDate, cardCvv, cardBalance
  } = value;

  try {
    const { card, createError } = await cardsService
      .createCard(cardNumber, cardHolder, cardExpirationDate, cardCvv, cardBalance);

    if (createError) {
      return res.status(HTTP_STATUS_BAD_REQUEST).json(createError);
    }
    return res.status(HTTP_STATUS_CREATED).json(card);
  }
  catch (err) {
    return res.status(HTTP_STATUS_INTERNAL_SERVER_ERROR).json({ error: err.message });
  }
};

module.exports = {
  getCards,
  createCard
};
