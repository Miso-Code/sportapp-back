const { DataTypes } = require('sequelize');
const { sequelize } = require('../db');
const { SubscriptionTypeEnum } = require('./enums');

const User = sequelize.define(
  'User',
  {
    user_id: {
      type: DataTypes.UUID,
      primaryKey: true,
      allowNull: false,
      defaultValue: DataTypes.UUIDV4
    },
    first_name: {
      type: DataTypes.STRING,
      allowNull: false
    },
    last_name: {
      type: DataTypes.STRING,
      allowNull: false
    },
    email: {
      type: DataTypes.STRING,
      allowNull: false
    },
    hashed_password: {
      type: DataTypes.STRING,
      allowNull: false
    },
    subscription_type: {
      type: DataTypes.ENUM(...Object.values(SubscriptionTypeEnum)),
      allowNull: false,
      defaultValue: SubscriptionTypeEnum.FREE
    }
  },
  {
    tableName: 'users',
    timestamps: false,
    underscored: true
  }
);

module.exports = User;
