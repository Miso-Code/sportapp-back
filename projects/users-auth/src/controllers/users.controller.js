const usersService = require('../services/user.service');
const { userSchema, loginSchema } = require('../models/schemas');

const register = async (req, res) => {
  const { error, value } = userSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ error: error.message });
  }
  try {
    const user = await usersService.registerUser(value);
    return res.status(201).json(user);
  }
  catch (e) {
    return res.status(400).json({ error: e.message });
  }
};

const login = async (req, res) => {
  const { error, value } = loginSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ error: error.message });
  }
  try {
    const user = await usersService.loginUser(value);
    return res.status(200).json(user);
  }
  catch (e) {
    return res.status(400).json({ error: e.message });
  }
};

module.exports = {
  register, login
};
