const Sequelize = require('sequelize');
const createSequelizeInstance = require('../db');

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
    jest.resetModules();
  });

  it('should initialize Sequelize with correct parameters in test environment', () => {
    const env = {
      NODE_ENV: 'test'
    };

    createSequelizeInstance(env);

    expect(Sequelize)
      .toHaveBeenCalledWith({
        dialect: 'sqlite',
        storage: ':memory:',
        logging: false
      });
  });

  it('should initialize Sequelize with correct parameters in dev environment', () => {
    const env = {
      NODE_ENV: 'other',
      DB_HOST: 'localhost',
      DB_USERNAME: 'testUser',
      DB_PASSWORD: 'testPass',
      DB_PORT: '5432',
      DB_NAME: 'testDb'
    };

    createSequelizeInstance(env);

    const URI = `postgres://${env.DB_USERNAME}:${env.DB_PASSWORD}@${env.DB_HOST}:${env.DB_PORT}/${env.DB_NAME}`;

    expect(Sequelize)
      .toHaveBeenCalledWith(URI, { logging: false });
  });

  it('should initialize Sequelize with correct parameters in aws environment', () => {
    const env = {
      NODE_ENV: 'aws',
      DB_HOST: 'localhost.amazonaws.com',
      DB_USERNAME: 'testUser',
      DB_PASSWORD: 'testPass',
      DB_PORT: '5432',
      DB_NAME: 'testDb'
    };

    createSequelizeInstance(env);

    expect(Sequelize)
      .toHaveBeenCalledWith({
        dialect: 'postgres',
        host: env.DB_HOST,
        username: env.DB_USERNAME,
        password: env.DB_PASSWORD,
        database: env.DB_NAME,
        logging: false,
        dialectOptions: {
          ssl: {
            rejectUnauthorized: false
          }
        }
      });
  });

  it('should initialize Sequelize with correct parameters with default values for non-test env', () => {
    const env = {
      NODE_ENV: 'other'
    };
    createSequelizeInstance(env);

    const URI = 'postgres://postgres:postgres@localhost:5432/postgres';

    expect(Sequelize)
      .toHaveBeenCalledWith(URI, { logging: false });
  });
});
