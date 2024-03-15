// takes a list of values and sorts based on that list
export default (arr, order) =>
  arr.sort((a, b) => order.indexOf(a) - order.indexOf(b))
