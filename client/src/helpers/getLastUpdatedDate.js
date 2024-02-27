// (resources)
// MDN toISOString: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString
// Test your regex https://regex101.com/
/*
@name getLastUpdatedDate
@description replaces the '<!-- Last Updated... -->' string in the given markdown and returns the last updated date string in YYYY-MM-DD format (UTC timezone)
e.g. ) Last Updated: YYYY-MM-DD
@param {string label - a label for the current date. If none, pass an empty string
*/

// a regex pattern for '<!-- Last Updated: (Month DD, YYYY || YYYY-MM-DD) -->'
const regex =
  /(<!--)\s*(Last Updated:)\s*(((\b\d{1,2}\D{0,3})?\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(Nov|Dec)(?:ember)?)\D?(\d{1,2}(st|nd|rd|th)?)?(([,.\-/])\D?)?((20\d{2})|\d{2})*)|\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01]))\s*(-->)/

export const getLastUpdatedDate = (markdown, env) => {
  return markdown.replace(
    regex,
    `Last Updated: ${env || new Date().toISOString().substring(0, 10)}`
  )
}

export default getLastUpdatedDate
