import { objectContains } from 'helpers/objectContains'
/**
 * @name filterWhere
 * @param {any[]} arr - an array of objects to be searched
 * @param {object} where - an object used to filter 'arr' (its value can be a string or a string of an array).
 * @return {any[]}
 * @description returns a new array of 'arr' containing elements with only matching properties
 * @usage
 * filterWhere([ {a:'a', b:'b'}, {a:'a', b:'b'}, {b:'b', c:'c'} ], {a: 'a'}) // [ { a : 'a', b: 'b' }, { a : 'a',  b : 'b' } ]
 * filterWhere([ {a:'a', b:'b'}, {a:'b', b:'b'}, {a:'a', c:'c'} ], {a: ['a', 'b']}) // [ { a : 'a', b: 'b' }, { a : 'b',  b : 'b' }, { a : 'a', c: 'c' }
 */
export const filterWhere = (arr = [], where = {}) =>
  arr.filter((obj) => {
    return Object.keys(where).every((key) => {
      const value = where[key]
      // If the value in where is an array, check if the object's key matches any of the values in the array
      if (Array.isArray(value)) {
        return value.includes(obj[key])
      }

      return objectContains(obj, { [key]: value })
    })
  })

export default filterWhere
