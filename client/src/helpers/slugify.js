/*
@name slugify
@description slugifies the given string
@param {string} str - a string to be slugified
*/
export const slugify = (str) => {
  const space = /\s+/g

  return str
    .toLowerCase()
    .replace(/[^a-zA-Z ]/g, '')
    .replace(space, ' ')
    .trim()
    .replace(space, '-')
}

export default slugify
