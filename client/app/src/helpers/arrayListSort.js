/**
 * @name arrayListSort
 * @param {(string | number)[]} arr - an array of values to be sorted
 * @param {(string | number)[]} order - an array containing sort order
 * @return {(string | number)[]}
 * @description returns the sorted array based on 'order'
 * @usage
 * arrayListSort([ 'b', 'e', 'a', 'd', 'c' ], [ 'a', 'b', 'c', 'd', 'e' ]) // ['a', 'b', 'c', 'd', 'e' ]
 */
export const arrayListSort = (arr, order) =>
  arr.sort((a, b) => order.indexOf(a) - order.indexOf(b))

export default arrayListSort
