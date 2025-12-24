export const sortOnKeyByOrder = (items, key, sortOrder) => {
  return items.sort((a, b) => {
    return sortOrder.indexOf(a[key]) - sortOrder.indexOf(b[key])
  })
}
export default sortOnKeyByOrder
