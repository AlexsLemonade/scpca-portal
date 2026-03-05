/**
 *  @name differenceArray
 *  @param {(string | number)[]} arr - an array to be filtered
 *  @param {(string | number)[]} arrToCompare - an array to compare against
 *  @return {(string | number)[]} - a new array containing unique values from arr that are not in arrToCompare
 *  @description return the unique values from arr that are not in arrToCompare
 *  @usage
 *  differenceArray([2, 1], [2, 3]) // [1]
 */

export const differenceArray = (arr, arrToCompare) => {
  const compareSet = new Set(arrToCompare)
  return [...new Set(arr)].filter((e) => !compareSet.has(e))
}

export default differenceArray
