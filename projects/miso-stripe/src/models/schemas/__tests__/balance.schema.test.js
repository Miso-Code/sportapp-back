const { balanceSchema } = require('../balance.schema');

describe('Balance Schema', () => {
  it('should validate a valid balance object', () => {
    const validData = {
      cardNumber: '1234567890123456',
      amount: 100
    };

    const { error } = balanceSchema.validate(validData);

    expect(error)
      .toBeFalsy();
  });

  it('should not validate if cardNumber is missing', () => {
    const invalidData = {
      amount: 100
    };

    const { error } = balanceSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"cardNumber" is required');
  });

  it('should not validate if amount is missing', () => {
    const invalidData = {
      cardNumber: '1234567890123456'
    };

    const { error } = balanceSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"amount" is required');
  });

  it('should not validate if cardNumber is not 16 characters long', () => {
    const invalidData = {
      cardNumber: '123456789012345',
      amount: 100
    };

    const { error } = balanceSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"cardNumber" length must be 16 characters long');
  });

  it('should not validate if amount is not a positive number', () => {
    const invalidData = {
      cardNumber: '1234567890123456',
      amount: -100
    };

    const { error } = balanceSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"amount" must be a positive number');
  });
});
