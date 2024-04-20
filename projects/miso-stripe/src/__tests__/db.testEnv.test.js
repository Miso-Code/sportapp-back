const Sequelize = require('sequelize');

jest.mock('sequelize', () => jest.fn()
  .mockImplementation(() => ({
    authenticate: jest.fn()
      .mockResolvedValue(),
    define: jest.fn(),
    sync: jest.fn()
      .mockResolvedValue()
  })));

describe('Database Connection', () => {
  it('should initialize Sequelize with correct parameters in test environment', () => {
    process.env.NODE_ENV = 'test';

    // eslint-disable-next-line global-require
    require('../db');

    expect(Sequelize)
      .toHaveBeenCalledWith({
        dialect: 'sqlite',
        storage: ':memory:',
        logging: false
      });
  });
});
