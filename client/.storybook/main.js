const path = require('path')
const Dotenv = require('dotenv-webpack')

const envVars = {
  API_HOST: 'http://localhost:8000',
  API_VERSION: 'v1'
}

module.exports = {
  addons: ['@storybook/addon-storysource'],
  staticDirs: ['./../public'],
  stories: ['./stories/**/*.stories.@(js|mdx)'],
  webpackFinal: async (config) => {
    // Add src to imports (so this works with app webpack config)
    config.resolve.modules.push(path.resolve(__dirname, './../src'))

    // Add env vars for helpers
    Object.keys(envVars).forEach((key) => {
      config.plugins.DefinePlugin.definitions[`process.env.${key}`] =
        JSON.stringify(envVars[key])
    })

    return config
  }
}
