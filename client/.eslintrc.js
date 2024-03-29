const path = require('path')

module.exports = {
  parser: '@babel/eslint-parser',
  parserOptions: {
    ecmaVersion: 6,
    sourceType: 'module',
    ecmaFeatures: {
      modules: true
    },
    babelOptions: {
      configFile: path.resolve(`${__dirname}/.babelrc.js`)
    }
  },
  extends: [
    'airbnb',
    'plugin:prettier/recommended',
    'plugin:storybook/recommended'
  ],
  env: {
    browser: true,
    es6: true
  },
  plugins: ['react'],
  rules: {
    camelcase: 'warn',
    'max-len': [
      'warn',
      {
        code: 80,
        tabWidth: 2,
        comments: 80,
        ignoreComments: true, // let's disable warnings on the comments
        ignoreTrailingComments: true,
        ignoreUrls: true,
        ignoreStrings: true,
        ignoreTemplateLiterals: true,
        ignoreRegExpLiterals: true
      }
    ],
    'jsx-a11y/href-no-hash': ['off'],
    'react/jsx-filename-extension': ['warn', { extensions: ['.js', '.jsx'] }],
    'react/jsx-one-expression-per-line': 0,
    'no-console': ['error', { allow: ['error'] }], // only allow `console.error` calls
    'no-unused-vars': 2,
    'no-func-assign': 0,

    // Not sure if we should enforce these rules.
    'class-methods-use-this': 0,
    'react/prop-types': 0,
    'no-nested-ternary': 'warn',
    'no-class-assign': 0,
    'no-restricted-syntax': 0,
    'no-continue': 0,
    'react/destructuring-assignment': 0,
    'react/no-unescaped-entities': 0,
    'jsx-a11y/click-events-have-key-events': 0,
    'import/prefer-default-export': 0,
    'no-use-before-define': 0,
    'react/no-multi-comp': 0,
    'import/no-mutable-exports': 0,
    'react/jsx-props-no-spreading': 'warn'
  },
  settings: {
    'import/resolver': {
      node: {
        moduleDirectory: ['node_modules', 'src']
      }
    }
  }
}
