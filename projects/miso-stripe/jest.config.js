/** @type {import('jest').Config} */
const config = {
  testEnvironment: 'node',
  clearMocks: true,
  coverageDirectory: 'coverage',
  coverageProvider: 'v8',
  collectCoverageFrom: ['src/**/*.js'],
  moduleFileExtensions: ['js'],
  testMatch: ['**/*.test.js'],
  coveragePathIgnorePatterns: [
    'node_modules',
    '__tests__',
    'app.js',
    'index.js'
  ],
  testPathIgnorePatterns: [
    '/node_modules/'
  ]
};

module.exports = config;
