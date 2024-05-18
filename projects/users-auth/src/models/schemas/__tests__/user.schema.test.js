const userSchema = require('../user.schema');

describe('User Schema', () => {
  it('should validate a valid user object', () => {
    const validData = {
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@example.com',
      password: 'password123'
    };

    const { error } = userSchema.validate(validData);

    expect(error).toBeFalsy();
  });

  it('should not validate if first_name is missing', () => {
    const invalidData = {
      last_name: 'Doe',
      email: 'john.doe@example.com',
      password: 'password123'
    };

    const { error } = userSchema.validate(invalidData);

    expect(error).toBeTruthy();
    expect(error.details[0].message).toContain('"first_name" is required');
  });

  it('should not validate if last_name is missing', () => {
    const invalidData = {
      first_name: 'John',
      email: 'john.doe@example.com',
      password: 'password123'
    };

    const { error } = userSchema.validate(invalidData);

    expect(error).toBeTruthy();
    expect(error.details[0].message).toContain('"last_name" is required');
  });

  it('should not validate if email is missing', () => {
    const invalidData = {
      first_name: 'John',
      last_name: 'Doe',
      password: 'password123'
    };

    const { error } = userSchema.validate(invalidData);

    expect(error).toBeTruthy();
    expect(error.details[0].message).toContain('"email" is required');
  });

  it('should not validate if email is not a valid email format', () => {
    const invalidData = {
      first_name: 'John',
      last_name: 'Doe',
      email: 'invalid-email',
      password: 'password123'
    };

    const { error } = userSchema.validate(invalidData);

    expect(error).toBeTruthy();
    expect(error.details[0].message).toContain('"email" must be a valid email');
  });

  it('should not validate if password is missing', () => {
    const invalidData = {
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@example.com'
    };

    const { error } = userSchema.validate(invalidData);

    expect(error).toBeTruthy();
    expect(error.details[0].message).toContain('"password" is required');
  });
});
