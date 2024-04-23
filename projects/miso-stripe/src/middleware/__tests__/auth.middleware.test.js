const { HTTP_STATUS_UNAUTHORIZED } = require('http2').constants;
const authMiddleware = require('../auth.middleware');

describe('authMiddleware', () => {
  let req;
  let res;
  let next;

  beforeEach(() => {
    req = { get: jest.fn() };
    res = {
      status: jest.fn()
        .mockReturnThis(),
      send: jest.fn()
    };
    next = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should call next() if API key matches', async () => {
    const apiKey = 'correctApiKey';
    process.env.API_KEY = apiKey;
    req.get.mockReturnValueOnce(apiKey);

    await authMiddleware(req, res, next);

    expect(req.get)
      .toHaveBeenCalledWith('api_key');
    expect(next)
      .toHaveBeenCalledTimes(1);
  });

  it('should return HTTP_STATUS_UNAUTHORIZED if API key does not match', async () => {
    const apiKey = 'correctApiKey';
    process.env.API_KEY = apiKey;
    req.get.mockReturnValueOnce('wrongApiKey');

    await authMiddleware(req, res, next);

    expect(req.get)
      .toHaveBeenCalledWith('api_key');
    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_UNAUTHORIZED);
    expect(res.send)
      .toHaveBeenCalledWith('Not authenticated');
    expect(next)
      .not
      .toHaveBeenCalled();
  });

  it('should return HTTP_STATUS_UNAUTHORIZED if API key is missing', async () => {
    process.env.API_KEY = 'correctApiKey';
    req.get.mockReturnValueOnce(undefined);

    await authMiddleware(req, res, next);

    expect(req.get)
      .toHaveBeenCalledWith('api_key');
    expect(res.status)
      .toHaveBeenCalledWith(HTTP_STATUS_UNAUTHORIZED);
    expect(res.send)
      .toHaveBeenCalledWith('Not authenticated');
    expect(next)
      .not
      .toHaveBeenCalled();
  });
});
