// This is a simple loader used with raw-loader for importing
// markdown to be consumed by grommet/Markdown

module.exports = (source) => {
  // eslint-disable-next-line
  return eval(`\`${source}\``)
}
