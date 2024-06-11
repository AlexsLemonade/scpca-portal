import React from 'react'
import { Download as DownloadIcon } from 'grommet-icons'
import { useMetadataOnly } from 'hooks/useMetadataOnly'
import { DownloadModal } from 'components/DownloadModal'

export const MetadataDownloadModal = ({ project, disabled }) => {
  const { isMetadataOnlyAvailable, metadataComputedFile } = useMetadataOnly(
    project.computed_files
  )

  return (
    <DownloadModal
      disabled={!isMetadataOnlyAvailable || disabled}
      icon={<DownloadIcon color="brand" />}
      resource={project}
      publicComputedFile={metadataComputedFile}
      sampleMetadataOnly
    />
  )
}

export default MetadataDownloadModal
