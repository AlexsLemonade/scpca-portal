/*
@name getDefaultComputedFile
@description returns the first element of the computed_files array fetched from the API
@param {Object} resource - a resource object that contains a computed_files array
*/
export const getDefaultComputedFile = (resource) => {
  return resource.computed_files[0]
}

export default getDefaultComputedFile
