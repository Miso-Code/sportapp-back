const { transactionSchema } = require('../transaction.schema');

describe('Transaction Schema', () => {
  it('should validate a valid transaction object', () => {
    const validData = {
      cardNumber: '1234567890123456',
      cardHolder: 'John Doe',
      cardExpirationDate: '12/24',
      cardCvv: '123',
      amount: 100
    };

    const { error } = transactionSchema.validate(validData);

    expect(error)
      .toBeFalsy();
  });

  it('should not validate if cardNumber is missing', () => {
    const invalidData = {
      cardHolder: 'John Doe',
      cardExpirationDate: '12/24',
      cardCvv: '123',
      amount: 100
    };

    const { error } = transactionSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"cardNumber" is required');
  });

  it('should not validate if cardHolder is missing', () => {
    const invalidData = {
      cardNumber: '1234567890123456',
      cardExpirationDate: '12/24',
      cardCvv: '123',
      amount: 100
    };

    const { error } = transactionSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"cardHolder" is required');
  });

  it('should not validate if cardExpirationDate is missing', () => {
    const invalidData = {
      cardNumber: '1234567890123456',
      cardHolder: 'John Doe',
      cardCvv: '123',
      amount: 100
    };

    const { error } = transactionSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"cardExpirationDate" is required');
  });

  it('should not validate if cardCvv is missing', () => {
    const invalidData = {
      cardNumber: '1234567890123456',
      cardHolder: 'John Doe',
      cardExpirationDate: '12/24',
      amount: 100
    };

    const { error } = transactionSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"cardCvv" is required');
  });

  it('should not validate if amount is missing', () => {
    const invalidData = {
      cardNumber: '1234567890123456',
      cardHolder: 'John Doe',
      cardExpirationDate: '12/24',
      cardCvv: '123'
    };

    const { error } = transactionSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"amount" is required');
  });

  it('should not validate if cardNumber is not 16 characters long', () => {
    const invalidData = {
      cardNumber: '123456789012345',
      cardHolder: 'John Doe',
      cardExpirationDate: '12/24',
      cardCvv: '123',
      amount: 100
    };

    const { error } = transactionSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"cardNumber" length must be 16 characters long');
  });

  it('should not validate if cardExpirationDate is not in the MM/YY format', () => {
    const invalidData = {
      cardNumber: '1234567890123456',
      cardHolder: 'John Doe',
      cardExpirationDate: '2024/12',
      cardCvv: '123',
      amount: 100
    };

    const { error } = transactionSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"cardExpirationDate" with value "2024/12" fails to match the required pattern');
  });

  it('should not validate if cardCvv is not 3 digits long', () => {
    const invalidData = {
      cardNumber: '1234567890123456',
      cardHolder: 'John Doe',
      cardExpirationDate: '12/24',
      cardCvv: '12',
      amount: 100
    };

    const { error } = transactionSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"cardCvv" with value "12" fails to match the required pattern');
  });

  it('should not validate if amount is not a positive number', () => {
    const invalidData = {
      cardNumber: '1234567890123456',
      cardHolder: 'John Doe',
      cardExpirationDate: '12/24',
      cardCvv: '123',
      amount: -100
    };

    const { error } = transactionSchema.validate(invalidData);

    expect(error)
      .toBeTruthy();
    expect(error.details[0].message)
      .toContain('"amount" must be a positive number');
  });
});
