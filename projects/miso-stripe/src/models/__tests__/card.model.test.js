const Card = require('../card.model');

describe('Card Model', () => {
  it('should define a Card model with the correct attributes', () => {
    const modelAttributes = Card.tableAttributes;

    expect(modelAttributes.cardNumber)
      .toHaveProperty('allowNull', false);
    expect(modelAttributes.cardNumber)
      .toHaveProperty('primaryKey', true);

    expect(modelAttributes.cardHolder)
      .toHaveProperty('allowNull', false);

    expect(modelAttributes.cardExpirationDate)
      .toHaveProperty('allowNull', false);

    expect(modelAttributes.cardCvv)
      .toHaveProperty('allowNull', false);

    expect(modelAttributes.cardBalance)
      .toHaveProperty('allowNull', false);
  });
});
