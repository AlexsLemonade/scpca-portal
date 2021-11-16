// convert object to query string ie: ?key=val
// optional keys list to prevent passing all object keys

export const urlSearchParamsFromKeys = (query, ...keys) => {
  const search = new URLSearchParams()

  const appendParam = (key, val) => {
    if (keys.length === 0 || keys.includes(key)) {
      if (Array.isArray(val)) {
        val.forEach((v) => appendParam(key, v))
      } else {
        search.append(key, val)
      }
    }
  }

  Object.entries(query).forEach((entry) => appendParam(...entry))

  return search
}

export default urlSearchParamsFromKeys
