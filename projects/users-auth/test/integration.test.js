const request = require('supertest');
const app = require('../src/app');
const { sequelize } = require('../src/db');
const User = require('../src/models/user.model');
const { hashPassword } = require('../src/utils');

const requestToEndpoint = (url, method) => request(app)[method](url);

const USER_AUTH_BASE_URL = '/auth';

describe('Users Integration Tests', () => {
  let fakeUser;

  beforeEach(async () => {
    fakeUser = {
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@example.com',
      password: 'password'
    };
    process.env.NODE_ENV = 'test';
    await sequelize.authenticate();
    await User.sync({ force: true });
  });

  afterEach(async () => {
    await User.drop();
  });

  describe('POST /register', () => {
    it('should register a new user and return 201', async () => {
      const response = await requestToEndpoint(`${USER_AUTH_BASE_URL}/register`, 'post')
        .send(fakeUser);

      expect(response.statusCode).toEqual(201);
      expect(response.body).toHaveProperty('user_id');
      expect(response.body).toHaveProperty('first_name', fakeUser.first_name);
      expect(response.body).toHaveProperty('last_name', fakeUser.last_name);
      expect(response.body).toHaveProperty('email', fakeUser.email);
    });

    it('should return 400 if user already exists', async () => {
      const hashedPassword = hashPassword(fakeUser.password);
      await User.create({
        first_name: fakeUser.first_name,
        last_name: fakeUser.last_name,
        email: fakeUser.email,
        hashed_password: hashedPassword
      });

      const response2 = await requestToEndpoint(`${USER_AUTH_BASE_URL}/register`, 'post')
        .send(fakeUser);

      expect(response2.statusCode).toEqual(400);
      expect(response2.body).toHaveProperty('error', 'User already exists');
    });
  });

  describe('POST /login', () => {
    it('should login a user and return access tokens', async () => {
      const hashedPassword = hashPassword(fakeUser.password);
      await User.create({
        first_name: fakeUser.first_name,
        last_name: fakeUser.last_name,
        email: fakeUser.email,
        hashed_password: hashedPassword
      });

      const response = await requestToEndpoint(`${USER_AUTH_BASE_URL}/login`, 'post')
        .send({ email: fakeUser.email, password: fakeUser.password });

      expect(response.statusCode).toEqual(200);
      expect(response.body).toHaveProperty('user_id');
      expect(response.body).toHaveProperty('access_token');
      expect(response.body).toHaveProperty('access_token_expires_minutes');
      expect(response.body).toHaveProperty('refresh_token');
      expect(response.body).toHaveProperty('refresh_token_expires_minutes');
    });

    it('should return 400 if user does not exist', async () => {
      const response = await requestToEndpoint(`${USER_AUTH_BASE_URL}/login`, 'post')
        .send({ email: 'nonexistent@example.com', password: fakeUser.password });

      expect(response.statusCode).toEqual(400);
      expect(response.body).toHaveProperty('error', 'User does not exist');
    });

    it('should return 400 if password is incorrect', async () => {
      const hashedPassword = hashPassword(fakeUser.password);
      await User.create({
        first_name: fakeUser.first_name,
        last_name: fakeUser.last_name,
        email: fakeUser.email,
        hashed_password: hashedPassword
      });
      const response = await requestToEndpoint(`${USER_AUTH_BASE_URL}/login`, 'post')
        .send({ email: fakeUser.email, password: 'wrong_password' });

      expect(response.statusCode).toEqual(400);
      expect(response.body).toHaveProperty('error', 'Invalid password');
    });
  });
});
