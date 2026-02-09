import * as path from 'path'

const envVars = {
  API_HOST: 'http://localhost:8000',
  API_VERSION: 'v1'
}

module.exports = {
  addons: [
    // '@storybook/addon-storysource',
    // '@storybook/addon-links',
    '@storybook/addon-essentials'
  ],
  framework: {
    name: '@storybook/react-webpack5',
    options: {}
  },
  staticDirs: ['../../public'],
  stories: ['./stories/**/*.stories.@(js|mdx)'],

  webpackFinal: async (config) => {
    // Add src to imports (so this works with app webpack config)
    config.resolve.modules.push(path.resolve(__dirname, '../../src'))
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      data: path.resolve(__dirname, './data'),
      '@client': path.resolve(__dirname, '../../src'),
      components: path.resolve(__dirname, '../../src/components'),
      contexts: path.resolve(__dirname, '../../src/contexts'),
      hooks: path.resolve(__dirname, '../../src/hooks')
    }

    config.resolve.fallback = {
      ...(config.resolve.fallback || {}),
      zlib: false
    }

    config.module.rules.push({
      test: /\.(js|jsx)$/,
      exclude: /node_modules/,
      use: {
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-react']
        }
      }
    })

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
