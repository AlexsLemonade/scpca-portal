import { filterWhere } from 'helpers/filterWhere'

// TODO: Implement the logic to handle multiple metadata files (i.e. project and portal-wide) later
export const useMetadataOnly = (computedFiles) => {
  const metadataComputedFile = filterWhere(computedFiles, {
    metadata_only: true
  })
  // Check the availability of metadata_only file
  const isMetadataOnlyAvailable = metadataComputedFile.length > 0

  // NOTE: The current logic only supports the project level metadata file,
  // thus the first item is returned
  return {
    metadataComputedFile: metadataComputedFile[0],
    isMetadataOnlyAvailable
  }
}

export default useMetadataOnly
