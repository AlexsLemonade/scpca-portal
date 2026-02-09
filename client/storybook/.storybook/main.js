import * as path from 'path'

const envVars = {
  API_HOST: 'http://localhost:8000',
  API_VERSION: 'v1'
}

module.exports = {
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-interactions'
  ],
  framework: {
    name: '@storybook/nextjs',
    options: {}
  },
  staticDirs: ['../../public'],
  stories: ['./stories/**/*.stories.@(js|mdx)'],

  webpackFinal: async (config) => {
    // Add src to imports (so this works with app webpack config)
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      data: path.resolve(__dirname, './data'),
      components: path.resolve(__dirname, '../../src/components'),
      contexts: path.resolve(__dirname, '../../src/contexts'),
      hooks: path.resolve(__dirname, '../../src/hooks')
    }

    // Add env vars for helpers
    config.plugins.forEach((plugin) => {
      if (Object.keys(plugin)[0] === 'definitions') {
        Object.keys(envVars).forEach((key) => {
          plugin['definitions'][`process.env.${key}`] = JSON.stringify(
            envVars[key]
          )
        })
      }
    })

    return config
  }
}
