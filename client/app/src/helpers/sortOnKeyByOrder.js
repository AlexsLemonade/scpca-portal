export const sortOnKeyByOrder = (items, key, sortOrder) =>
  items.sort((a, b) => sortOrder.indexOf(a[key]) - sortOrder.indexOf(b[key]))
export default sortOnKeyByOrder
