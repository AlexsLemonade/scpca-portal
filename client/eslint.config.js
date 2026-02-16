import path from 'path'
import { fileURLToPath } from 'url'
import { FlatCompat } from '@eslint/eslintrc'
import babelParser from '@babel/eslint-parser'
import globals from 'globals'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const compat = new FlatCompat({
  baseDirectory: __dirname
})

export default [
  // Ignore patterns
  {
    ignores: ['cellbrowser/']
  },
  // Legacy configs
  ...compat.extends(
    'airbnb',
    'plugin:prettier/recommended',
    'plugin:storybook/recommended'
  ),
  // Project rules
  {
    languageOptions: {
      parser: babelParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        requireConfigFile: true,
        babelOptions: {
          configFile: path.resolve(`${__dirname}/.babelrc.js`)
        }
      },
      globals: {
        ...globals.browser,
        ...globals.es2021
      }
    },

    rules: {
      // JS correctness, safety, styling and formatting
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

      'default-param-last': 'warn',
      'no-class-assign': 'off',
      'no-console': ['error', { allow: ['error'] }], // only allow `console.error` calls
      'no-continue': 'off',
      'no-func-assign': 'off',
      'no-nested-ternary': 'warn',
      'no-promise-executor-return': 'warn',
      'no-restricted-syntax': 'off',
      'no-unsafe-optional-chaining': 'warn',
      'no-unused-vars': 'error',
      'no-use-before-define': 'off',

      // React correctness, safety, styling and formatting
      'react/destructuring-assignment': 'off',
      'react/function-component-definition': [
        'warn',
        {
          namedComponents: 'arrow-function',
          unnamedComponents: 'arrow-function'
        }
      ],
      'react/jsx-filename-extension': ['warn', { extensions: ['.js', '.jsx'] }],
      'react/jsx-no-useless-fragment': 'warn',
      'react/jsx-no-constructed-context-values': 'warn',
      'react/jsx-one-expression-per-line': 'off',
      'react/jsx-props-no-spreading': 'warn',
      'react/no-multi-comp': 'off',
      'react/no-unescaped-entities': 'off',
      'react/no-unstable-nested-components': ['warn', { allowAsProps: true }],
      'react/prop-types': 'off',

      'jsx-a11y/href-no-hash': 'off',
      'jsx-a11y/click-events-have-key-events': 'off',

      // Relax Airbnb strictness
      'class-methods-use-this': 'off',
      'import/no-mutable-exports': 'off',
      'import/prefer-default-export': 'off'
    },

    settings: {
      'import/resolver': {
        node: {
          moduleDirectory: ['node_modules', 'src']
        }
      }
    }
  }
]
