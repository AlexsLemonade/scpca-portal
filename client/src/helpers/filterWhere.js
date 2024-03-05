import objectContains from "helpers/objectContains"
/*
  Takes an array of objects and filters on filter object keys and values.
*/

export default (objectArray = [], where = {}) => {
  return objectArray.filter((obj) => objectContains(obj, where))
}
