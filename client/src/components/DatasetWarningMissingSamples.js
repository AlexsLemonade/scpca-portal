import React from 'react'

import { WarningText } from 'components/WarningText'

export const DatasetWarningMissingSamples = ({ project, sampleCount }) => {
  return (
    <WarningText
      text={`Selected modalities may not be available for ${sampleCount} ${
        sampleCount > 1 ? 'samples' : 'sample'
      }.`}
      link={`/projects/${project.scpca_id}`}
      linkLabel="Inspect"
      newTab
    />
  )
}

export default DatasetWarningMissingSamples
