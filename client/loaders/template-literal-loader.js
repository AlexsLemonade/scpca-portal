// This is a simple loader used with raw-loader for importing
// markdown to be consumed by grommet/Markdown
// escape backticks to prevent build errors
// TODO: Update to support blocked (ie: ```)

module.exports = (source) => {
  const formatted = source.replace(/`/g, '\\`')
  // eslint-disable-next-line
  return eval(`\`${formatted}\``)
}
