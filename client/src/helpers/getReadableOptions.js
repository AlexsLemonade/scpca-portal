import { getReadable } from 'helpers/getReadable'
/**
 * @name getReadableOptions
 * @param {string[]} options - an array of values (for 'readableNames' in 'getReadable')
 * @return {any[]}}
 * @description returns a non-duplicate array of objects. Each object contains the 'label' and 'value'
 * that are generally used for selects/dropdowns UIs.
 * @usage
 * getReadableOptions([ 'SINGLE_CELL', 'MULTIPLEXED', 'NOT_IN_THE_LIST' ])
 * It returns the label and value for a dropdown in the download modal:
 * [
 *   { label: "Single-cell", value: "SINGLE_CELL" },
 *   { label: "Multiplexed", value :"MULTIPLEXED" },
 *   { label: "NOT_IN_THE_LIST", value :"NOT_IN_THE_LIST" }
 * ]
 */
export const getReadableOptions = (options = []) =>
  [...new Set(options)].map((option) => ({
    label: getReadable(option),
    value: option
  }))

export default getReadableOptions
