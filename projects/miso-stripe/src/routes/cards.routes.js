const { Router } = require('express');

const router = new Router();
const cardsController = require('../controllers/cards.controller');

router.get('/', cardsController.getCards);
router.post('/', cardsController.createCard);

module.exports = router;
