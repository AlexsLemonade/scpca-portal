import * as path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const envVars = {
  API_HOST: 'http://localhost:8000',
  API_VERSION: 'v1'
}

export default {
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
      api: path.resolve(__dirname, '../../src/api'),
      components: path.resolve(__dirname, '../../src/components'),
      contexts: path.resolve(__dirname, '../../src/contexts'),
      hooks: path.resolve(__dirname, '../../src/hooks'),
      helpers: path.resolve(__dirname, '../../src/helpers')
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

    // Customize svg rules, code used from https://storybook.js.org/docs/get-started/frameworks/nextjs#custom-webpack-config
    config.module = config.module || {}
    config.module.rules = config.module.rules || []

    // This modifies the existing image rule to exclude .svg files
    // since you want to handle those files with @svgr/webpack
    const imageRule = config.module.rules.find((rule) => rule?.['test']?.test('.svg'));
    if (imageRule) {
      imageRule['exclude'] = /\.svg$/;
    }

    // Configure .svg files to be loaded with @svgr/webpack
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });



    return config
  }
}
