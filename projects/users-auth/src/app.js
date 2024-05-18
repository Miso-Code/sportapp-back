const express = require('express');
const morgan = require('morgan');
const bodyParser = require('body-parser');

const app = express();
const { User } = require('./models');

User.sync();
app.use(bodyParser.json());
app.use(morgan('dev'));

const usersRouter = require('./routes/users.routes');

app.use('/auth', usersRouter);
app.use('/ping', (req, res) => res.status(200)
  .json({
    message: 'User Registration Service'
  }));

module.exports = app;
