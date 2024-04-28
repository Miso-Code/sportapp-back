const {
  HTTP_STATUS_OK,
  HTTP_STATUS_INTERNAL_SERVER_ERROR,
  HTTP_STATUS_BAD_REQUEST
} = require('http2').constants;

const { balanceSchema } = require('../models/schemas/balance.schema');
const balancesService = require('../services/balances.service');

const addBalanceToCard = async (req, res) => {
  const { error, value } = balanceSchema.validate(req.body);

  if (error) {
    return res.status(HTTP_STATUS_BAD_REQUEST).json({ error: error.message });
  }

  const { amount, cardNumber } = value;

  try {
    const { succeed, depositResponse } = await balancesService.deposit(cardNumber, amount);

    if (!succeed) {
      return res.status(HTTP_STATUS_BAD_REQUEST).json(depositResponse);
    }

    return res.status(HTTP_STATUS_OK).json(depositResponse);
  }
  catch (err) {
    return res.status(HTTP_STATUS_INTERNAL_SERVER_ERROR).json({ error: err.message });
  }
};

const removeBalanceToCard = async (req, res) => {
  const { error, value } = balanceSchema.validate(req.body);

  if (error) {
    return res.status(HTTP_STATUS_BAD_REQUEST).json({ error: error.message });
  }

  const { amount, cardNumber } = value;

  try {
    const { succeed, withdrawResponse } = await balancesService.withdraw(cardNumber, amount);

    if (!succeed) {
      return res.status(HTTP_STATUS_BAD_REQUEST).json(withdrawResponse);
    }

    return res.status(HTTP_STATUS_OK).json(withdrawResponse);
  }
  catch (err) {
    return res.status(HTTP_STATUS_INTERNAL_SERVER_ERROR).json({ error: err.message });
  }
};

module.exports = {
  addBalanceToCard,
  removeBalanceToCard
};
