import { objectContains } from 'helpers/objectContains'
/**
 * @name filterWhere
 * @param {any[]} arr - an array of objects to be searched
 * @param {object} where - an object used to filter 'arr'
 * @return {any[]}
 * @description returns a new array of 'arr' containing elements with only matching properties
 * @usage
 * filterWhere([ {a:'a', b:'b'}, {a:'a', b:'b'}, {b:'b', c:'c'} ], {a: "a"}) // [ { a : "a", b: "b" }, { a : "a",  b : "b" } ]
 */
export const filterWhere = (arr = [], where = {}) => {
  return arr.filter((obj) => objectContains(obj, where))
}

export default filterWhere
