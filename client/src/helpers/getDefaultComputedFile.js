import { objectContains } from 'helpers/objectContains'

/*
@name getDefaultComputedFile
@description returns the first element of the computed_files array fetched from the API
@param {Object} resource - a resource object that contains a computed_files array
@param {String} modality - a resource object that contains a computed_files array
*/
export const getDefaultComputedFile = (
  resource,
  computedFile,
  constraints = {}
) => {
  const { computed_files: computedFiles } = resource
  if (!computedFile) return computedFiles[0]

  const { modality, format } = computedFile

  const filter = { modality, format, ...constraints }

  const defaultFile = computedFiles.find((file) => objectContains(file, filter))

  return defaultFile || computedFiles[0]
}

export default getDefaultComputedFile
