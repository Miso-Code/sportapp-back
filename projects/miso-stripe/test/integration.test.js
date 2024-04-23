const request = require('supertest');

const falso = require('@ngneat/falso');
const app = require('../src/app');
const { sequelize } = require('../src/db');
const { Card } = require('../src/models');

const requestWithHeaders = (url, method) => request(app)[method](url)
  .set('api_key', 'test');

describe('Integration Tests', () => {
  let fakeCard;
  beforeEach(async () => {
    fakeCard = falso.randCreditCard({ brand: 'Visa' });
    fakeCard.number = fakeCard.number.replace(/ /g, '');
    process.env.NODE_ENV = 'test';
    process.env.API_KEY = 'test';
    await sequelize.authenticate();
    await Card.sync();
    await Card.destroy({ where: {} });
  });

  describe('Cards', () => {
    describe('when calling the Create endpoint', () => {
      it('should return 201 and create a new Card', async () => {
        const cardData = {
          cardNumber: fakeCard.number,
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv
        };
        const response = await requestWithHeaders('/miso-stripe/cards', 'post')
          .send(cardData);

        expect(response.statusCode)
          .toEqual(201);

        expect(response.body)
          .toEqual({
            cardNumber: fakeCard.number,
            cardHolder: fakeCard.fullName,
            cardExpirationDate: fakeCard.untilEnd,
            cardCvv: fakeCard.ccv,
            cardBalance: 0
          });
      });

      it('should return 400 if the card number is invalid', async () => {
        const cardData = {
          cardNumber: '1234',
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv
        };
        const response = await requestWithHeaders('/miso-stripe/cards', 'post')
          .send(cardData);

        expect(response.statusCode)
          .toEqual(400);

        expect(response.body)
          .toEqual({
            error: '"cardNumber" length must be 16 characters long'
          });
      });

      it('should return 400 if the card expiration date is invalid', async () => {
        const cardData = {
          cardNumber: fakeCard.number,
          cardHolder: fakeCard.fullName,
          cardExpirationDate: '12/20',
          cardCvv: fakeCard.ccv
        };
        const response = await requestWithHeaders('/miso-stripe/cards', 'post')
          .send(cardData);

        expect(response.statusCode)
          .toEqual(400);

        expect(response.body)
          .toEqual({
            message: 'Card has expired'
          });
      });
    });

    describe('whe calling the Get All endpoint', () => {
      it('should return 200 and retrieve all cards', async () => {
        await Card.create({
          cardNumber: fakeCard.number,
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv,
          cardBalance: 0
        });

        const response = await requestWithHeaders('/miso-stripe/cards', 'get');

        expect(response.statusCode)
          .toEqual(200);

        expect(response.body)
          .toEqual([{
            cardNumber: fakeCard.number,
            cardHolder: fakeCard.fullName,
            cardExpirationDate: fakeCard.untilEnd,
            cardCvv: fakeCard.ccv,
            cardBalance: 0
          }]);
      });
    });
  });

  describe('Payments', () => {
    describe('when calling Payment endpoint', () => {
      it('should return 200 and process a payment', async () => {
        await Card.create({
          cardNumber: fakeCard.number,
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv,
          cardBalance: 100
        });

        const paymentData = {
          cardNumber: fakeCard.number,
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv,
          amount: 50
        };

        const response = await requestWithHeaders('/miso-stripe/payments', 'post')
          .send(paymentData);

        expect(response.statusCode)
          .toEqual(200);

        expect(response.body)
          .toEqual({
            message: 'Payment processed successfully'
          });
      });

      it('should return 400 if the card has wrong information', async () => {
        const paymentData = {
          cardNumber: '1234',
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv,
          amount: 50
        };
        const response = await requestWithHeaders('/miso-stripe/payments', 'post')
          .send(paymentData);

        expect(response.statusCode)
          .toEqual(400);

        expect(response.body)
          .toEqual({
            error: '"cardNumber" length must be 16 characters long'
          });
      });

      it('should return 400 if the card has insufficient balance', async () => {
        await Card.create({
          cardNumber: fakeCard.number,
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv,
          cardBalance: 0
        });

        const paymentData = {
          cardNumber: fakeCard.number,
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv,
          amount: 50
        };

        const response = await requestWithHeaders('/miso-stripe/payments', 'post')
          .send(paymentData);

        expect(response.statusCode)
          .toEqual(400);

        expect(response.body)
          .toEqual({
            error: 'Insufficient funds'
          });
      });
    });
  });

  describe('Balances', () => {
    describe('when calling Add Balance endpoint', () => {
      it('should return 200 and add balance to a card', async () => {
        await Card.create({
          cardNumber: fakeCard.number,
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv,
          cardBalance: 0
        });

        const balanceData = {
          cardNumber: fakeCard.number,
          amount: 50
        };

        const response = await requestWithHeaders('/miso-stripe/balances/add', 'post')
          .send(balanceData);

        expect(response.statusCode)
          .toEqual(200);

        expect(response.body)
          .toEqual({
            message: `Deposit of $${balanceData.amount} for card ${balanceData.cardNumber} succeed`
          });
      });

      it('should return 400 if the card has wrong information', async () => {
        const balanceData = {
          cardNumber: '1234',
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv,
          amount: 50
        };
        const response = await requestWithHeaders('/miso-stripe/balances/add', 'post')
          .send(balanceData);

        expect(response.statusCode)
          .toEqual(400);

        expect(response.body)
          .toEqual({
            error: '"cardNumber" length must be 16 characters long'
          });
      });
    });

    describe('when calling Remove Balance endpoint', () => {
      it('should return 200 and remove balance from a card', async () => {
        await Card.create({
          cardNumber: fakeCard.number,
          cardHolder: fakeCard.fullName,
          cardExpirationDate: fakeCard.untilEnd,
          cardCvv: fakeCard.ccv,
          cardBalance: 100
        });

        const balanceData = {
          cardNumber: fakeCard.number,
          amount: 50
        };

        const response = await requestWithHeaders('/miso-stripe/balances/remove', 'post')
          .send(balanceData);

        expect(response.statusCode)
          .toEqual(200);

        expect(response.body)
          .toEqual({
            message: `Withdraw of $${balanceData.amount} for card ${balanceData.cardNumber} succeed`
          });
      });

      it('should return 400 if the card has wrong information', async () => {
        const balanceData = {
          cardNumber: '1234',
          amount: 50
        };
        const response = await requestWithHeaders('/miso-stripe/balances/remove', 'post')
          .send(balanceData);

        expect(response.statusCode)
          .toEqual(400);

        expect(response.body)
          .toEqual({
            error: '"cardNumber" length must be 16 characters long'
          });
      });
    });
  });
});
