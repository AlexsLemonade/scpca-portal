/*
@name hasMultiple
@description returns true if an array contains more than one element, otherwise false
@param {any[]} a - an array to be checked
@param {function} filter - optional filter function to be applied to the array
*/
export const hasMultiple = (a, filter) => {
  const arr = filter ? a.filter(filter) : a
  return arr.length > 1
}

export default hasMultiple
