/**
 *  @name pluralize
 *  @param {string} defaultStr - a default string used for singular format
 *  @param {number} count - a count that determines the pluralization
 *  @param {string} customStr - (optional) a custom override string for plural format
 *  @return {string} - a formatted pluralized string
 *  @description returns a formatted pluralized string based on the given count
 *  @usage
 *  pluralize('One Sample', 1, `${count} Samples`) // One Sample
 *  pluralize("One Sample", 2, `${count} Samples`) // 2 Samples
 *  pluralize(`${count} Project`, 1) // 1 Project
 *  pluralize(`${count} Project`, 3) // 3 Projects
 */
export const pluralize = (defaultStr, count, customStr = '') => {
  if (count === 1) return defaultStr

  return customStr || `${defaultStr}s`
}

export default pluralize
