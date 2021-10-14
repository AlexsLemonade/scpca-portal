/**
 * Capitalizes first letters of words in string.
 * @param {string} str String to be modified
 * @param {boolean=false} lower Whether all other letters should be lowercased
 * @return {string}
 * @usage
 *   capitalize('fix this string');     // -> 'Fix This String'
 *   capitalize('javaSCrIPT');          // -> 'JavaSCrIPT'
 *   capitalize('javaSCrIPT', true);    // -> 'Javascript'
 */
export const capitalize = (string, lower = false) => {
  const str = string || ''
  return (lower ? str.toLowerCase() : str).replace(
    /(?:^|\s|["'([{])+\S/g,
    (match) => match.toUpperCase()
  )
}

export default capitalize
