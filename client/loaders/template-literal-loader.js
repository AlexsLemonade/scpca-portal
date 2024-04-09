// This is a simple loader used with raw-loader for importing
// markdown to be consumed by grommet/Markdown

module.exports = (source) => {
  // escape backticks to prevent build errors
  const formatted = source.replace(/[^\\]`/g, '\\`')

  // eslint-disable-next-line
  return eval(`\`${formatted}\``)
}
