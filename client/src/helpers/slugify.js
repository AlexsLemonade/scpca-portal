// Returns a valid id attribute name for HTML
export default (str) => {
  const space = /\s+/g

  return str
    .toLowerCase()
    .replace(/[^a-zA-Z ]/g, '')
    .replace(space, ' ')
    .replace(space, '-')
    .trim()
}
