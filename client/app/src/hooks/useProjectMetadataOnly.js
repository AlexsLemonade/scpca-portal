import { useEffect, useState } from 'react'
import { filterWhere } from 'helpers/filterWhere'

export const useProjectMetadataOnly = (project) => {
  const metadataOnlyKey = { metadata_only: true }
  const [metadataComputedFiles, setMetadataComputedFiles] = useState([])
  const isMetadataOnlyAvailable = metadataComputedFiles.length > 0

  // Set states for the project metedata
  useEffect(() => {
    setMetadataComputedFiles(
      filterWhere(project.computed_files, metadataOnlyKey)
    )
  }, [project])

  return {
    metadataComputedFile: metadataComputedFiles[0],
    isMetadataOnlyAvailable
  }
}

export default useProjectMetadataOnly
