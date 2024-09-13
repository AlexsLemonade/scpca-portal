import React from 'react'
import { usePortalMetadataOnly } from 'hooks/usePortalMetadataOnly'
import { DownloadModal } from 'components/DownloadModal'

export const PortalMetadataDownload = () => {
  const {
    resource,
    portalMetadataComputedFile,
    isPortalMetadataOnlyAvailable
  } = usePortalMetadataOnly()

  return (
    <>
      {resource && portalMetadataComputedFile && (
        <DownloadModal
          label="Get All Sample Metadata"
          resource={resource}
          publicComputedFile={portalMetadataComputedFile}
          disabled={!isPortalMetadataOnlyAvailable}
        />
      )}
    </>
  )
}

export default PortalMetadataDownload
