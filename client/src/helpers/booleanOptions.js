export const booleanOptions = ['Yes', 'No', 'Not Specified']

export const getBooleanString = (value) => {
  if (value === true) return booleanOptions[0]
  if (value === false) return booleanOptions[1]
  if (value === null) return booleanOptions[2]
  return undefined
}

export const getBooleanValue = (string) => {
  if (string === booleanOptions[0]) return true
  if (string === booleanOptions[1]) return false
  if (string === booleanOptions[2]) return null
  return undefined
}
