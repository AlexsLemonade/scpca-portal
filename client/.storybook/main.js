const path = require('path')
const Dotenv = require('dotenv-webpack')

const envVars = {
  API_HOST: 'http://localhost:8000',
  API_VERSION: 'v1'
}

module.exports = {
  stories: ['./stories/**/*.stories.@(js|mdx)'],
  addons: ['@storybook/addon-storysource'],
  webpackFinal: async (config) => {
    // Add src to imports (so this works with app webpack config)
    config.resolve.modules.push(path.resolve(__dirname, './../src'))

    // Add env vars for helpers
    const plugin = config.plugins.find(
      (plugin) => plugin.definitions?.['process.env']
    )

    Object.keys(envVars).forEach((key) => {
      plugin.definitions['process.env'][key] = JSON.stringify(envVars[key])
    })

    return config
  }
}
