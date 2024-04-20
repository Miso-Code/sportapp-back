const {
  HTTP_STATUS_OK,
  HTTP_STATUS_INTERNAL_SERVER_ERROR,
  HTTP_STATUS_BAD_REQUEST
} = require('http2').constants;
const { transactionSchema } = require('../models/schemas/transaction.schema');
const transactionsService = require('../services/transactions.service');

const cardPayment = async (req, res) => {
  const { error, value } = transactionSchema.validate(req.body);

  if (error) {
    return res.status(HTTP_STATUS_BAD_REQUEST).json({ error: error.message });
  }

  const {
    cardNumber, cardHolder, cardExpirationDate, cardCvv, amount
  } = value;

  try {
    const {
      succeed,
      paymentResponse
    } = await transactionsService
      .processPayment(cardNumber, cardHolder, cardExpirationDate, cardCvv, amount);

    if (!succeed) {
      return res.status(HTTP_STATUS_BAD_REQUEST).json(paymentResponse);
    }

    return res.status(HTTP_STATUS_OK).json(paymentResponse);
  }
  catch (err) {
    return res.status(HTTP_STATUS_INTERNAL_SERVER_ERROR).json({ error: err.message });
  }
};

module.exports = {
  cardPayment
};
