/**
 *  @name getHashMap
 *  @param {object[]} items - an array of objects that include the lookup key
 *  @param {string} key - the key to use for mapping each object
 *  @return {string} - an object mapping the 'key' value to the corresponding item in the given array
 *  @description returns a hashmap where each key is the value of the given key in the array items
 *  @usage
 *  const arr = [{id: 'p1', name: 'a'}, {id: 'p2', name: 'b'}]
 *  getHashMap(arr, 'id') // { p1: {id: 'p1', name: 'a'}, p2: {id: 'p1', name: 'b'} }
 */

export const getHashMap = (items, key) =>
  items.reduce((acc, cur) => {
    acc[cur[key]] = cur
    return acc
  }, {})

export default getHashMap
