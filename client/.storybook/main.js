import * as path from 'path'

const envVars = {
  API_HOST: process.env.API_HOST || 'http://localhost:8000',
  API_VERSION: process.env.API_VERSION || 'v1'
}

export default {
  addons: [
    '@storybook/addon-storysource',
    '@storybook/addon-links',
    '@storybook/addon-essentials',
  ],
  framework: {
    name: '@storybook/nextjs',
    options: {}
  },
  staticDirs: ['./../public'],
  stories: ['./stories/**/*.stories.@(js|mdx)'],

  webpackFinal: async (config) => {
    // Add src to imports (so this works with app webpack config)
    config.resolve.modules.push(path.resolve(__dirname, './../src'))
    config.resolve.alias['data'] = path.resolve(__dirname, './data')

    // As webpack 5 and on don't include polyfills, disable the unnecessary error
    config.resolve.fallback = {
      ...(config.resolve.fallback || {}),
      zlib: false
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

    // Add custom svg loading rule (taken from next.config.js file)
    const svgLoaderRule = config.module.rules.find((r) =>
      r.test?.test?.('.svg')
    )
    if (!svgLoaderRule) {
      throw new Error('Could not find Next.js file loader rule for SVGs.')
    }
    // append `?url` to the import for an image source url
    svgLoaderRule.resourceQuery = /url/

    config.module.rules.push({
      test: /\.svg$/i,
      issuer: /\.[jt]sx?$/,
      resourceQuery: { not: /url/ },
      use: [
        {
          loader: '@svgr/webpack',
          options: {
            svgoConfig: {
              plugins: [
                {
                  name: 'preset-default',
                  params: {
                    overrides: {
                      cleanupIds: false,
                      removeViewBox: false
                    }
                  }
                },
                {
                  name: 'prefixIds',
                  params: {
                    prefix: true
                  }
                }
              ]
            }
          }
        }
      ]
    })

    return config
  }
}
