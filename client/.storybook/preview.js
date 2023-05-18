const { default: theme } = require('./decorators/theme')
const { default: context } = require('./decorators/context')
const { RouterContext } = require('next/dist/shared/lib/router-context')
module.exports = {
  decorators: [theme, context],
  parameters: {
    nextRouter: {
      Provider: RouterContext.Provider
    }
  }
}
