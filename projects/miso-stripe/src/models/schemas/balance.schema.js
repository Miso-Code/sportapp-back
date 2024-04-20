const Joi = require('joi');

const balanceSchema = Joi.object({
  cardNumber: Joi.string().required().length(16), amount: Joi.number().required().positive()
});

module.exports = {
  balanceSchema
};
