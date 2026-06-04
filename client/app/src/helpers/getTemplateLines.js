import escapeBackticks from 'helpers/escapeBackticks'

// Returns an array of template strings ready for Markdown component
// NOTE: This function calls `eval` and therefore *must* never be called on user entered input.
export default (contentString, newLineChar = '\\n') =>
  contentString.split(newLineChar).map((line) =>
    // biome-ignore lint/security/noGlobalEval: markdown needs to be evaled
    eval(`\`${escapeBackticks(line.trim())}\``)
  )
