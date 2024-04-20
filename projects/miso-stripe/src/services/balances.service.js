const { Card } = require('../models');

async function deposit(cardNumber, amount) {
  const card = await Card.findOne({ where: { cardNumber } });

  if (!card) {
    return {
      succeed: false,
      depositResponse: { error: 'Card not found' }
    };
  }

  await card.increment('cardBalance', { by: amount });
  return {
    succeed: true,
    depositResponse: { message: `Deposit of $${amount} for card ${cardNumber} succeed` }
  };
}

async function withdraw(cardNumber, amount) {
  const card = await Card.findOne({ where: { cardNumber } });

  if (!card) {
    return {
      succeed: false,
      withdrawResponse: { error: 'Card not found' }
    };
  }

  if (card.cardBalance < amount) {
    return {
      succeed: false,
      withdrawResponse: { error: 'Insufficient funds' }
    };
  }

  await card.decrement('cardBalance', { by: amount });
  return {
    succeed: true,
    withdrawResponse: { message: `Withdraw of $${amount} for card ${cardNumber} succeed` }
  };
}

module.exports = {
  deposit,
  withdraw
};
