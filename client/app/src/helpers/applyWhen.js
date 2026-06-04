// Helper for conditionally applying rules in theme

export const applyWhen = (evaluation, rule) => (evaluation ? rule : '')

export default applyWhen
