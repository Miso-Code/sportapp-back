const Joi = require('joi');

const transactionSchema = Joi.object(
  {
    cardNumber: Joi.string()
      .required()
      .length(16),
    cardHolder: Joi.string()
      .required(),
    cardExpirationDate: Joi.string()
      .required()
      .regex(/^(0[1-9]|1[0-2])\/\d{2}$/),
    cardCvv: Joi.string()
      .required()
      .regex(/^\d{3}$/),
    amount: Joi.number()
      .required()
      .positive()
  }
);

module.exports = {
  transactionSchema
};
