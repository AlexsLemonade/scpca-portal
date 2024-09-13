import React from 'react'
import { useMetadataOnly } from 'hooks/useMetadataOnly'
import { DownloadModal } from 'components/DownloadModal'

export const PortalMetadataDownload = () => {
  const {
    resource,
    portalMetadataComputedFile,
    isPortalMetadataOnlyAvailable
  } = useMetadataOnly()

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
