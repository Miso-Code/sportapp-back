const express = require('express');
const morgan = require('morgan');
const bodyParser = require('body-parser');
const authMiddleware = require('./middleware/auth.middleware');

const app = express();
const { Card } = require('./models');

Card.sync();
app.use(bodyParser.json());
app.use(authMiddleware);
app.use(morgan('dev'));

const balancesRouter = require('./routes/balances.routes');
const paymentsRouter = require('./routes/payments.routes');
const cardRouter = require('./routes/cards.routes');

app.use('/miso-stripe/payments', paymentsRouter);
app.use('/miso-stripe/balances', balancesRouter);
app.use('/miso-stripe/cards', cardRouter);
app.use('/ping', (req, res) => res.status(200)
  .json({
    message: 'Miso Stripe Service'
  }));

module.exports = app;
