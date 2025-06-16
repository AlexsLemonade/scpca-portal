/*
@name filterOut
@description returns a new array excluding the given values
@param {any[]} arr - an array to be filtered
@param {...any} values - one or more values to be filtered out from the array
@returns {any[]} a filtered array without the given values
*/
export const filterOut = (arr, ...values) =>
  arr.filter((a) => !values.includes(a))
