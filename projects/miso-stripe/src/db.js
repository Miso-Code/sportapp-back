const Sequelize = require('sequelize');

let sequelize;
if (process.env.NODE_ENV === 'test') {
  sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: ':memory:',
    logging: false
  });
}
else {
  const config = {
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASS || 'postgres',
    port: process.env.DB_PORT || '5432',
    db: process.env.DB_NAME || 'postgres'
  };
  const URI = `postgres://${config.user}:${config.password}@${config.host}:${config.port}/${config.db}`;
  sequelize = new Sequelize(URI, { logging: false });
}

module.exports = sequelize;
