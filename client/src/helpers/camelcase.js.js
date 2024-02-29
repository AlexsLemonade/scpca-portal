/*
@name camelcase
@description converts the given string to camelcase
@param {str} str - a string to be converted
*/
export const camelcase = (str) => {
  const formattedStr = str
    .replaceAll('&', 'And')
    .replace(/[^a-zA-Z ]/g, '')
    .split(' ')
    .map((x) => `${x.charAt(0).toUpperCase()}${x.substring(1)}`)
    .join('')

  return `${formattedStr.charAt(0).toLowerCase()}${formattedStr.substring(1)}`
}

export default camelcase
