const init = require('../server');
const { sequelize } = require('../db');
const app = require('../app');

jest.mock('../db', () => ({
  sequelize: {
    authenticate: jest.fn()
  }
}));

jest.mock('../app', () => ({
  listen: jest.fn()
}));

describe('Initialization Function', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should call sequelize.authenticate', async () => {
    await init();
    expect(sequelize.authenticate)
      .toHaveBeenCalled();
  });

  it('should call app.listen', async () => {
    await init();
    expect(app.listen)
      .toHaveBeenCalledWith(8000, expect.any(Function));
  });

  it('should exit the process if an error occurs', async () => {
    const exitSpy = jest.spyOn(process, 'exit')
      .mockImplementation(() => {
      });
    const consoleSpy = jest.spyOn(console, 'error')
      .mockImplementation(() => {
      });
    const error = new Error('Test Error');
    sequelize.authenticate.mockRejectedValueOnce(error);

    await init();
    expect(exitSpy)
      .toHaveBeenCalledWith(1);
    expect(consoleSpy)
      .toHaveBeenCalledWith(`An error occurred: ${JSON.stringify(error)}`);

    exitSpy.mockRestore();
    consoleSpy.mockRestore();
  });
});
