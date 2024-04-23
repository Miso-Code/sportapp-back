const { DataTypes } = require('sequelize');
const { sequelize } = require('../db');

const Card = sequelize.define('Card', {
  cardNumber: {
    type: DataTypes.STRING,
    allowNull: false,
    primaryKey: true
  },
  cardHolder: {
    type: DataTypes.STRING,
    allowNull: false
  },
  cardExpirationDate: {
    type: DataTypes.STRING,
    allowNull: false
  },
  cardCvv: {
    type: DataTypes.STRING,
    allowNull: false
  },
  cardBalance: {
    type: DataTypes.DECIMAL,
    allowNull: false
  }
}, {
  tableName: 'credit_cards',
  timestamps: false
});

module.exports = Card;
