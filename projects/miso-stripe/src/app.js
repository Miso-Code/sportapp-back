const express = require('express');
const bodyParser = require('body-parser');
const authMiddleware = require('./middleware/auth.middleware');

const app = express();
const { Card } = require('./models');

Card.sync();
app.use(bodyParser.json());
app.use(authMiddleware);

const balancesRouter = require('./routes/balances.routes');
const paymentsRouter = require('./routes/payments.routes');
const cardRouter = require('./routes/cards.routes');

app.use('/miso-stripe/payments', paymentsRouter);
app.use('/miso-stripe/balances', balancesRouter);
app.use('/miso-stripe/cards', cardRouter);

module.exports = app;
