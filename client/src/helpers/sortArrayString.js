/*
@name sortArrayString
@description returns the sorted given array of strings alphabetically in ascending or descending order
@param {string[]} arr - an array of strings to sort
@param {boolean} desc - if true, sorts in descending order, otherwise, ascending
@returns {string[]} the sorted given array
*/
export const sortArrayString = (arr, desc = false) =>
  arr.sort((a, b) => {
    const sorted = a.localeCompare(b, undefined, { sensitivity: 'base' })
    return desc ? -sorted : sorted
  })
