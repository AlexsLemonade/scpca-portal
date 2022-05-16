/*
@param value - an array or a single value
@param key - a key that is used for calculation
*/
export const accumulateValue = (value, key) =>
  [...value].reduce((prev, curr) => prev[key] + curr[key])
