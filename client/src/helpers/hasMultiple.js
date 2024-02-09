/*
@name hasMultiple
@description returns true if an array contains more than one element, otherwise false
@param {any[]} a - an array to be checked
*/
export const hasMultiple = (a) => {
  return a.filter((cf) => cf.format !== 'ANN_DATA').length > 1
}

export default hasMultiple
