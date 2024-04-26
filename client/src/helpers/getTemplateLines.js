import escapeBackticks from 'helpers/escapeBackticks'

// Returns an array of template strings ready for Markdown component
export default (contentString, newLineChar = '\\n') =>
  contentString
    .split(newLineChar)
    .map((line) => eval(`\`${escapeBackticks(line.trim())}\``))
