/*
@name sortArrayByKey
@description sort an array or an array of object
@param {string} key - an object key that is used to sort
@param {array} target - an arry to sort
@param {array} sortOrder - a preferred sorting order
@param {boolean} asc - a boolean indicates whether it's ascending order or not
*/

export const sortArrayByKey = (
  key = '',
  target,
  sortOrder = [],
  asc = true
) => {
  const sortedArray = target.sort((a, b) => {
    if (sortOrder.length > 0) {
      return sortOrder.indexOf(a[key]) - sortOrder.indexOf(b[key])
    }

    return a[key] > b[key] ? 1 : -1
  })

  if (!asc) return sortedArray.reverse()

  return sortedArray
}
