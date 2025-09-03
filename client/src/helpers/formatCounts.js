import { getReadable } from 'helpers/getReadable'
/**
 *  @name formatCounts
 *  @description returns a new array of count strings from the given object.
 *  @param {object} obj - a counts object (e.g., { a: 5, b: 2, c: 11, d: 3 })
 *  @return {string[]} an array of formatted count object string (e.g., [" a (5)", "b (2)", "c (11)", "d (3)"])
 */

// Convert modality keys to human-readable before formatting
export const formatModalityCounts = (obj) =>
  Object.entries(obj).map(([k, v]) => `${getReadable(k)} (${v})`)

// Sort values in descending order, then sort keys in alphabetical order (case-insensitive)
export const formatDiagnosisCounts = (obj) =>
  Object.entries(obj)
    .sort(([aKey, aVal], [bKey, bVal]) => {
      if (aVal !== bVal) {
        return bVal - aVal
      }
      return aKey.localeCompare(bKey, undefined, { sensitivity: 'base' })
    })
    .map(([k, v]) => `${k} (${v})`)

export const formatCounts = (obj) =>
  Object.entries(obj).map(([k, v]) => `${k} (${v})`)
