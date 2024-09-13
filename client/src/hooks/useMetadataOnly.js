import { useEffect, useState } from 'react'
import { api } from 'api'
import { filterWhere } from 'helpers/filterWhere'

export const useMetadataOnly = (initialResource) => {
  const portalMetadataKey = { portal_metadata_only: true }
  const [resource, setResource] = useState(initialResource || {})
  const metadataComputedFiles = filterWhere(resource.computed_files, {
    metadata_only: true
  })
  const [portalMetadataComputedFiles, setPortalMetadataComputedFiles] =
    useState([])

  // Check the availability of metadata files
  const isMetadataOnlyAvailable = metadataComputedFiles.length > 0
  const isPortalMetadataOnlyAvailable = portalMetadataComputedFiles.length === 1

  const getPortalMetadataResource = async () => {
    const resourceRequest = await api.computedFiles.list(portalMetadataKey)
    return {
      resource: { computed_files: resourceRequest.response.results }
    }
  }

  // Configure State for portal metedata
  useEffect(() => {
    const getPortalMetadata = async () => {
      const response = await getPortalMetadataResource()
      setResource(response.resource)
      setPortalMetadataComputedFiles(
        filterWhere(response.resource.computed_files, portalMetadataKey)
      )
    }
    if (!initialResource) getPortalMetadata()
  }, [])

  return {
    resource,
    metadataComputedFile: metadataComputedFiles[0],
    portalMetadataComputedFile: portalMetadataComputedFiles[0],
    isMetadataOnlyAvailable,
    isPortalMetadataOnlyAvailable
  }
}

export default useMetadataOnly
