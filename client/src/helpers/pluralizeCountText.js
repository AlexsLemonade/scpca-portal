/**
 *  @name pluralizeCountText
 *  @param {number} count - a count that determines the pluralization of the text
 * @param {string} text - the text to pluralize
 *  @return {string} - a formatted pluralized text
 *  @description returns a formatted pluralized text based on the given count size
 *  @usage
 *  pluralizeCountText(1, 'Sample') // 1 Sample
 *  pluralizeCountText(3, 'project') // 3 projects
 */
export const pluralizeCountText = (count, text) =>
  `${count} ${text}${count > 1 ? 's' : ''}`

export default pluralizeCountText
