/**
 *  @name pick
 *  @param {any[]} arr - an array of objects
 *  @param {string} key - a key to find
 *  @return {any[]}
 *  @description returns a new array containing the value(s) of the given 'key' found in 'arr'
 *  @usage
 *  pick([{ a: 'a', b: 'b'}, {b: 'b', c: 'c'},{c: 'c', d: 'd'}], 'c' )) // ['c', 'c']
 *  pick(
 *    [
 *     { format: "SINGLE_CELL_EXPERIMENT" },
 *     { format: "ANN_DATA" }
 *    ], 'format'
 *   ) // [ 'SINGLE_CELL_EXPERIMENT', 'ANN_DATA' ]
 * */

export const pick = (arr = [], key) =>
  arr.reduce((acc, cur) => {
    if (cur[key]) acc.push(cur[key])
    return acc
  }, [])

export default pick
