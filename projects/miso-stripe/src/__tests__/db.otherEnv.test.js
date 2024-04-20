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
  afterEach(() => {
    jest.clearAllMocks();
    delete process.env.NODE_ENV;
    delete process.env.DB_HOST;
    delete process.env.DB_USER;
    delete process.env.DB_PASS;
    delete process.env.DB_PORT;
    delete process.env.DB_NAME;
  });

  it('should initialize Sequelize with correct parameters in non-test environment', () => {
    process.env.NODE_ENV = 'other';
    process.env.DB_HOST = 'localhost';
    process.env.DB_USER = 'testUser';
    process.env.DB_PASS = 'testPass';
    process.env.DB_PORT = '5432';
    process.env.DB_NAME = 'testDb';

    // eslint-disable-next-line global-require
    require('../db');

    const URI = 'postgres://testUser:testPass@localhost:5432/testDb';

    expect(Sequelize)
      .toHaveBeenCalledWith(URI, { logging: false });
  });
});
