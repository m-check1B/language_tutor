export default {
  transform: {
    '^.+\\.svelte$': 'svelte-jester',
    '^.+\\.ts$': 'ts-jest'
  },
  moduleFileExtensions: ['js', 'ts', 'svelte'],
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['@testing-library/jest-dom'],
  moduleNameMapper: {
    '^\\$app/(.*)$': '<rootDir>/.svelte-kit/runtime/app/$1',
    '^\\$lib/(.*)$': '<rootDir>/src/lib/$1'
  },
  extensionsToTreatAsEsm: ['.ts', '.svelte'],
  globals: {
    'ts-jest': {
      useESM: true,
    },
  },
};
