/**
 *  @name uniqueArray
 *  @param {(string | number)[]} arrs - one or more arrays to be filtered
 *  @return {(string | number)[]}
 *  @description returns a new array containing only the unique values from 'arrs'
 *  @usage
 *  uniqueArray([1,2,2,3,4,5,1,3,6]) // [1, 2, 3, 4, 5, 6]
 *  uniqueArray([1,2,2,3], [4,5,1,3,6]) // [1, 2, 3, 4, 5, 6]
 */
export const uniqueArray = (...arrs) => [...new Set(arrs.flat())]

export const uniqueArrayByKey = (arr, key) => {
  if (!key) return []

  const hash = arr.reduce((acc, current) => {
    const value = current[key]
    if (value && !acc[value]) {
      acc[value] = current
    }
    return acc
  }, {})

  return Object.values(hash)
}

export default uniqueArray
