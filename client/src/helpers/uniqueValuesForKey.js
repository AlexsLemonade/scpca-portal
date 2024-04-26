export default (items = [], key) => {
  return [...new Set(items.map((i) => i[key]))]
}
