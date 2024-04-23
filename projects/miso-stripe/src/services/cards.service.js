const { Card } = require('../models');

async function createCard(cardNumber, cardHolder, cardExpirationDate, cardCvv, cardBalance) {
  const cardExists = await Card.findOne({ where: { cardNumber } });

  if (cardExists) {
    return {
      card: null,
      createError: {
        message: 'Card already exists'
      }
    };
  }

  const currentYear = new Date().getFullYear()
    .toString()
    .slice(2);
  const currentMonth = new Date().getMonth() + 1;

  const [expirationMonth, expirationYear] = cardExpirationDate.split('/')
    .map(Number);

  if (
    expirationYear < currentYear
    || (expirationYear === currentYear && expirationMonth < currentMonth)
  ) {
    return {
      card: null,
      createError: {
        message: 'Card has expired'
      }
    };
  }

  const balance = cardBalance || 0;

  const card = Card.create({
    cardNumber,
    cardHolder,
    cardExpirationDate,
    cardCvv,
    cardBalance: balance
  });

  return {
    card: await card,
    createError: null
  };
}

async function getCards() {
  return Card.findAll();
}

module.exports = {
  createCard,
  getCards
};
