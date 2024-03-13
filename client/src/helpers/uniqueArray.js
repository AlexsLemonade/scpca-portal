/**
 *  @name uniqueArray
 *  @param {string|number[]} arr - an array to be filtered
 *  @return {(string | number)[]}
 *  @description returns a new array containing only the unique values of 'arr'
 *  @usage
 * uniqueArray([1,2,2,3,4,5,1,3,6]) // [1, 2, 3, 4, 5, 6]
 *
 */
export const uniqueArray = (arr) => [...new Set(arr)]

export default uniqueArray
