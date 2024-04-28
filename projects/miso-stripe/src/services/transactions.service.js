const { Card } = require('../models');

async function processPayment(cardNumber, cardHolder, cardExpirationDate, cardCvv, amount) {
  const card = await Card.findOne({ where: { cardNumber } });

  if (!card) {
    return { succeed: false, paymentResponse: { error: 'Card not found' } };
  }

  if (card.cardHolder.toLowerCase() !== cardHolder.toLowerCase().trim()) {
    return { succeed: false, paymentResponse: { error: 'Invalid card holder' } };
  }

  if (card.cardExpirationDate !== cardExpirationDate) {
    return { succeed: false, paymentResponse: { error: 'Invalid expiration date' } };
  }

  if (card.cardCvv !== cardCvv) {
    return { succeed: false, paymentResponse: { error: 'Invalid CVV' } };
  }

  if (card.cardBalance < amount) {
    return { succeed: false, paymentResponse: { error: 'Insufficient funds' } };
  }

  await card.decrement('cardBalance', { by: amount });
  return { succeed: true, paymentResponse: { message: 'Payment processed successfully' } };
}

module.exports = {
  processPayment
};
