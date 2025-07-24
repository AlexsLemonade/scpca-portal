/**
 * @name countArrayElements
 * @description counts the occurences of each element in the give array
 * @param {any[]} arr - an array of elements to be counted
 * @param {object} - returns an object where keys are elements and values are their counts
 * @usage
 * countArrayElements([1,2,2,3,4,5,1,3,6]) // { 1:2, 2:2, 3:2, 4:1, 5:1, 6:1 }
 */
export const countArrayElements = (arr) => {
  return arr.reduce((acc, cur) => {
    acc[cur] = (acc[cur] || 0) + 1
    return acc
  }, {})
}

export default countArrayElements
