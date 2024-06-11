import { filterWhere } from 'helpers/filterWhere'

// TODO: If necessary, add logic later or convert it to a helper file
export const useMetadataOnly = (computedFiles) => {
  // Check the availability of metadata_only file
  const isMetadataOnlyAvailable =
    filterWhere(computedFiles, {
      metadata_only: true
    }).length > 0

  const metadataComputedFile = filterWhere(computedFiles, {
    metadata_only: true
  })

  return {
    metadataComputedFile: metadataComputedFile[0],
    isMetadataOnlyAvailable
  }
}

export default useMetadataOnly
