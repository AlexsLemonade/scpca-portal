import escapeBackticks from 'helpers/escapeBackticks'

// Returns an array of template strings ready for Markdown component
// NOTE: This function calls `eval` and therefore *must* never be called on user entered input.
export default (contentString, newLineChar = '\\n') =>
  contentString
    .split(newLineChar)
    // eslint-disable-next-line no-eval
    .map((line) => eval(`\`${escapeBackticks(line.trim())}\``))
