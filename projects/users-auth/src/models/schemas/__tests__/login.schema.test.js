const loginSchema = require('../login.schema');

describe('Login Schema', () => {
  it('should validate with a valid email and password', () => {
    const validData = {
      email: 'test@example.com',
      password: 'password123'
    };

    const { error } = loginSchema.validate(validData);

    expect(error).toBeFalsy();
  });

  it('should validate with a valid refresh token', () => {
    const validData = {
      refresh_token: 'some-refresh-token'
    };

    const { error } = loginSchema.validate(validData);

    expect(error).toBeFalsy();
  });

  it('should not validate if both email and refresh token are provided', () => {
    const invalidData = {
      email: 'test@example.com',
      refresh_token: 'some-refresh-token'
    };

    const { error } = loginSchema.validate(invalidData);

    expect(error).toBeTruthy();
    expect(error.details[0].message).toContain('"value" contains a conflict between exclusive peers [email, refresh_token]');
  });

  it('should not validate if both password and refresh token are provided', () => {
    const invalidData = {
      password: 'password123',
      refresh_token: 'some-refresh-token'
    };

    const { error } = loginSchema.validate(invalidData);

    expect(error).toBeTruthy();
    expect(error.details[0].message).toContain('"password" missing required peer "email"');
  });

  it('should not validate if only email is provided without password', () => {
    const invalidData = {
      email: 'test@example.com'
    };

    const { error } = loginSchema.validate(invalidData);

    expect(error).toBeTruthy();
    expect(error.details[0].message).toContain('"email" missing required peer "password"');
  });

  it('should not validate if only password is provided without email', () => {
    const invalidData = {
      password: 'password123'
    };

    const { error } = loginSchema.validate(invalidData);

    expect(error).toBeTruthy();
    expect(error.details[0].message).toContain('"value" must contain at least one of [email, refresh_token]');
  });

  it('should not validate if email is not a valid email format', () => {
    const invalidData = {
      email: 'invalid-email',
      password: 'password123'
    };

    const { error } = loginSchema.validate(invalidData);

    expect(error).toBeTruthy();
    expect(error.details[0].message).toContain('"email" must be a valid email');
  });
});
