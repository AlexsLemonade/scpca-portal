import { getReadable } from 'helpers/getReadable'
/**
 *  @name formatCounts
 *  @description returns a new array of count strings from the given object. If formtKey is true, it formats the keys.
 *  @param {object} obj - a counts object (e.g., { a: 5, b: 2, c: 11, d: 3 })
 * @param {boolean} formatKey - a boolean flag determing whether to format the keys or not
 *  @return {string[]} an array of formatted count object string (e.g., [" a (5)", "b (2)", "c (11)", "d (3)"])
 */

export const formatCounts = (obj, formatKey = false) =>
  Object.entries(obj).map(
    ([k, v]) => `${formatKey ? getReadable(k) : k} (${v})`
  )
