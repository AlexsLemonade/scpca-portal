import { useEffect, useState } from 'react'
import { api } from 'api'

export const usePortalMetadataOnly = () => {
  const [portalMetadataComputedFiles, setPortalMetadataComputedFiles] =
    useState([])
  const isPortalMetadataOnlyAvailable = portalMetadataComputedFiles.length === 1

  // Set states for the portal metedata
  useEffect(() => {
    const getPortalMetadata = async () => {
      const resourceRequest = await api.computedFiles.list({
        portal_metadata_only: true
      })

      if (resourceRequest.isOk) {
        const { results } = resourceRequest.response
        setPortalMetadataComputedFiles(results)
      }
    }

    getPortalMetadata()
  }, [])

  return {
    portalMetadataComputedFile: portalMetadataComputedFiles[0],
    isPortalMetadataOnlyAvailable
  }
}

export default usePortalMetadataOnly
