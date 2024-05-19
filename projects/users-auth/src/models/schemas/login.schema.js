const Joi = require('joi');

const loginSchema = Joi.object({
  email: Joi.string().email(),
  password: Joi.string(),
  refresh_token: Joi.string()
}).xor('email', 'refresh_token')
  .with('email', 'password')
  .with('password', 'email')
  .without('email', 'refresh_token')
  .without('password', 'refresh_token');

module.exports = loginSchema;
