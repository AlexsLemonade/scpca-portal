import React from 'react'

import { WarningText } from 'components/WarningText'

export const DatasetWarningSpatialSamples = ({ sampleCount }) => {
  return (
    <WarningText
      text={`Selected modalities may not be available for ${sampleCount} ${
        sampleCount > 1 ? 'samples' : 'sample'
      }.`}
      link="/projects/SCPCP000006"
      linkLabel=" Inspect"
      newTab
    />
  )
}

export default DatasetWarningSpatialSamples
