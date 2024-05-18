const User = require('../user.model');

describe('User Model', () => {
  it('should define a User model with the correct attributes', () => {
    const modelAttributes = User.tableAttributes;

    expect(modelAttributes.user_id)
      .toHaveProperty('allowNull', false);
    expect(modelAttributes.user_id)
      .toHaveProperty('primaryKey', true);

    expect(modelAttributes.first_name)
      .toHaveProperty('allowNull', false);

    expect(modelAttributes.last_name)
      .toHaveProperty('allowNull', false);

    expect(modelAttributes.email)
      .toHaveProperty('allowNull', false);

    expect(modelAttributes.hashed_password)
      .toHaveProperty('allowNull', false);

    expect(modelAttributes.subscription_type)
      .toHaveProperty('allowNull', false);
  });
});
