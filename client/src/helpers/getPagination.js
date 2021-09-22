// helpers for handling pagination
export const offsetToPage = (offset, limit) => {
  return offset === 0 ? 1 : Math.ceil(offset / limit) + 1
}

export const pageToOffset = (page, limit) => {
  return page === 1 ? 0 : (page - 1) * limit
}

export const getLastIndex = (count, limit) => {
  if (!count) return 0
  return limit > 0 ? Math.floor(count / limit) : 0
}

export const pageToIndex = (page) => {
  return parseInt(page, 10) - 1
}

export const indexToPage = (index) => {
  return index + 1
}

export const countToLastOffset = (count, limit) => {
  return Math.ceil(count / limit) * limit - limit
}
