/*
@param arr - a targetd array that is iterlated over 
@param key - a key that is used to sort 
@param comp - an arary of prefered sorting order
@param asc - a boolean indicates whether it's ascending order or not
*/
export const sortArrayByKey = (arr, key, comp, asc = true) => {
  const sortedArray = [...arr].sort((a, b) => {
    if (Array.isArray(comp)) {
      return comp.indexOf(a[key]) - comp.indexOf[b[key]]
    }
    return a[key] > b[key] ? 1 : -1
  })

  if (!asc) return sortedArray.reverse()

  return sortedArray
}
