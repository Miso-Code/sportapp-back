const createSequelizeInstance = require('./db');

const sequelize = createSequelizeInstance();

module.exports = {
  sequelize,
  createSequelizeInstance
};
