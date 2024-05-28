/**
 * @name objectContains
 * @param {object} source - a base object to compare
 * @param {object} contains - an object to be matched
 * @return {boolean}
 * @description returns true if all properties of 'contains' are present in 'source'
 * @usage
 * objectContains({ a: 'a', b: 'b', c: 'c' }, { a: 'a', b: 'b' }) // true
 * objectContains({ a: 'a', b: 'b', c: 'c' }, { a: 'a', d: 'd' }) // false
 */
export const objectContains = (source, contains = {}) => {
  return !Object.entries(contains).find(([key, value]) => source[key] !== value)
}

export default objectContains
