// Helper for conditionally applying rules in theme

export default (evaluation, rule) => (evaluation ? rule : '')
