import { useEffect, useState } from 'react'
import { api } from 'api'
import { filterWhere } from 'helpers/filterWhere'

export const usePortalMetadataOnly = () => {
  const portalMetadataOnlyKey = { portal_metadata_only: true }
  const [portalMetadataComputedFiles, setPortalMetadataComputedFiles] =
    useState([])
  const isPortalMetadataOnlyAvailable = portalMetadataComputedFiles.length === 1

  // Set states for the portal metedata
  useEffect(() => {
    const getPortalMetadata = async () => {
      const resourceRequest = await api.computedFiles.list(
        portalMetadataOnlyKey
      )
      const { results } = resourceRequest.response
      setPortalMetadataComputedFiles(
        filterWhere(results, portalMetadataOnlyKey)
      )
    }

    getPortalMetadata()
  }, [])

  return {
    portalMetadataComputedFile: portalMetadataComputedFiles[0],
    isPortalMetadataOnlyAvailable
  }
}

export default usePortalMetadataOnly
