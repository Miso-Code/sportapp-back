const Sequelize = require('sequelize');

function createSequelizeInstance(envConfig = process.env) {
  let sequelize;

  if (envConfig.NODE_ENV === 'test') {
    sequelize = new Sequelize({
      dialect: 'sqlite',
      storage: ':memory:',
      logging: false
    });
  }
  else {
    const {
      DB_HOST,
      DB_USERNAME,
      DB_PASSWORD,
      DB_PORT,
      DB_NAME
    } = envConfig;
    const config = {
      host: DB_HOST || 'localhost',
      user: DB_USERNAME || 'postgres',
      password: DB_PASSWORD || 'postgres',
      port: DB_PORT || '5432',
      db: DB_NAME || 'postgres'
    };

    if (config.host.includes('amazonaws')) {
      sequelize = new Sequelize({
        logging: false,
        database: config.db,
        username: config.user,
        password: config.password,
        host: config.host,
        dialect: 'postgres',
        dialectOptions: {
          ssl: {
            rejectUnauthorized: false
          }
        }
      });
    }
    else {
      const URI = `postgres://${config.user}:${config.password}@${config.host}:${config.port}/${config.db}`;
      sequelize = new Sequelize(URI, {
        logging: false
      });
    }
  }

  return sequelize;
}

module.exports = createSequelizeInstance;
