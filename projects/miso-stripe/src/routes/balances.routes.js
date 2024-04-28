const { Router } = require('express');

const router = new Router();
const balancesController = require('../controllers/balances.controller');

router.post('/add', balancesController.addBalanceToCard);
router.post('/remove', balancesController.removeBalanceToCard);

module.exports = router;
