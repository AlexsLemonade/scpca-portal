/**
 * @name resetObjectFlags
 * @description reset all values of the given object's keys to the specified resetValue
 * @param {object} obj - the object to reset
 * @param {any} resetValue - the value to assign to all keys, false by default
 * @return {object} - a new object with all keys set to resetValue
 * @usage
 * resetObjectFlags({a: true, b: true, c: false}) // {a: false, b: false, c: false}
 */
export const resetObjectFlags = (obj, resetValue = false) =>
  Object.fromEntries(Object.keys(obj).map((k) => [k, resetValue]))
