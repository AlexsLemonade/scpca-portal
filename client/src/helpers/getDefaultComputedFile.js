/*
@name getDefaultComputedFile
@description returns the first element of the computed_files array fetched from the API
@param {Object} resource - a resource object that contains a computed_files array
@param {String} modality - a resource object that contains a computed_files array
*/
export const getDefaultComputedFile = (resource, computedFile) => {
  const { computed_files: computedFiles } = resource
  if (!computedFile) return computedFiles[0]

  const { modality: fileModality, format: fileFormat } = computedFile
  const defaultFile = computedFiles.find(
    ({ modality, format }) => modality === fileModality && format === fileFormat
  )
  return defaultFile || computedFiles[0]
}

export default getDefaultComputedFile
