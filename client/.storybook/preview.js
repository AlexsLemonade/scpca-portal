const { default: theme } = require('./decorators/theme')
const { default: context } = require('./decorators/context')

module.exports = {
  decorators: [theme, context]
}
