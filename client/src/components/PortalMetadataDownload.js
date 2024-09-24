import React from 'react'
import { usePortalMetadataOnly } from 'hooks/usePortalMetadataOnly'
import { DownloadModal } from 'components/DownloadModal'

export const PortalMetadataDownload = () => {
  const { portalMetadataComputedFile, isPortalMetadataOnlyAvailable } =
    usePortalMetadataOnly()

  return (
    <>
      <DownloadModal
        label="Get All Sample Metadata"
        publicComputedFile={portalMetadataComputedFile}
        disabled={!isPortalMetadataOnlyAvailable}
      />
    </>
  )
}

export default PortalMetadataDownload
