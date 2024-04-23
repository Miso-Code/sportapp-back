const { Router } = require('express');

const router = new Router();
const paymentsController = require('../controllers/payments.controller');

router.post('/', paymentsController.cardPayment);

module.exports = router;
