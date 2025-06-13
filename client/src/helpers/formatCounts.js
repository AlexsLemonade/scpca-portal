/*
@name formatCounts
@description returns a new array of count strings from the given object
@param {object} - a counts object (e.g., { a: 5, b: 2, c: 11, d: 3 })
@returns {string[]} an array of formatted count object (e.g., [" a (5)", "b (2)", "c (11)", "d (3)"])
*/
export const formatCounts = (obj) =>
  Object.entries(obj).map(([k, v]) => `${k} (${v})`)
