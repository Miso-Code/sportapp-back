const app = require('./app');
const { sequelize } = require('./db');

async function init() {
  try {
    await sequelize.authenticate();
    app.listen(8000, () => {
      console.log('Express App Listening on Port 8000');
    });
  }
  catch (error) {
    console.error(`An error occurred: ${JSON.stringify(error)}`);
    process.exit(1);
  }
}

module.exports = init;
