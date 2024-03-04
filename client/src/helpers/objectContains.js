/*
  Returns true if all key values in "contains" object
  match on source object
*/

export default (source, contains = {}) => {
  return !Object.entries(contains).find(([key, value]) =>
    source[key] != value
  )
}
