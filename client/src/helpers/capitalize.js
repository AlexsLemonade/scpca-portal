/**
 * Capitalizes first letters of words in string.
 * @param {string} str - string to be modified
 * @param {boolean} firstOnly - (optional) Whether to capitalize only the first letter of the first word
 * @param {boolean} lower - (optional) Whether all other letters should be lowercased
 * @return {string}
 * @usage
 *   By default:
 *   capitalize('fix this string');     // -> 'Fix This String'
 *   capitalize(' with space and "quotation" mark');     // -> 'With Space And "Quotation" Mark'
 *   With 'firstOnly':
 *   capitalize('fix this string', true);     // -> 'Fix this string'
 *   capitalize(' "quotation" mark with space', true);     // -> '"Quotation" mark with space'
 *   With 'lower':
 *   capitalize('javaSCrIPT', false, true);    // -> 'Javascript'
 */
export const capitalize = (str = '', firstOnly = false, lower = false) => {
  const re = new RegExp(/(?:^|\s|["'([{])+\S/, !firstOnly ? 'g' : '')

  return (lower ? str.toLowerCase() : str).replace(re, (match) =>
    match.toUpperCase()
  )
}

export default capitalize
