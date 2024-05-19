const { comparePassword, hashPassword } = require('../utils');
const User = require('../models/user.model');
const { decodeRefreshToken, generateTokens } = require('../security/jwt');

async function registerUser(user) {
  const existingUser = await User.findOne({ where: { email: user.email } });
  if (existingUser) {
    throw new Error('User already exists');
  }
  const hashedPassword = await hashPassword(user.password);
  const newUser = await User.create(
    {
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      hashed_password: hashedPassword
    }
  );

  return {
    user_id: newUser.user_id,
    first_name: newUser.first_name,
    last_name: newUser.last_name,
    email: newUser.email
  };
}

async function loginUser(userLoginData) {
  if (userLoginData.refreshToken) {
    try {
      const userId = decodeRefreshToken(userLoginData.refreshToken);
      const existingUser = await User.findOne({ where: { user_id: userId } });
      if (!existingUser) {
        throw new Error();
      }
      return generateTokens(userId, existingUser.subscription_type);
    }
    catch (err) {
      throw new Error('Invalid or expired refresh token');
    }
  }
  else {
    const existingUser = await User.findOne({ where: { email: userLoginData.email } });
    if (!existingUser) {
      throw new Error('User does not exist');
    }
    const isPasswordMatch = await comparePassword(
      userLoginData.password,
      existingUser.hashed_password
    );
    if (!isPasswordMatch) {
      throw new Error('Invalid password');
    }
    return generateTokens(existingUser.user_id, existingUser.subscription_type);
  }
}

module.exports = {
  registerUser, loginUser
};
