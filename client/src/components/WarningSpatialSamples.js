import React from 'react'
import { useDatasetOptionsContext } from 'hooks/useDatasetOptionsContext'
import { WarningText } from 'components/WarningText'

export const WarningSpatialSamples = () => {
  const { sampleDifferenceForSpatial, isSpatialSelected } =
    useDatasetOptionsContext()

  return (
    <>
      {isSpatialSelected && sampleDifferenceForSpatial !== 0 && (
        <WarningText
          text={`Selected modalities may not be available for ${sampleDifferenceForSpatial} ${
            sampleDifferenceForSpatial > 1 ? 'samples' : 'sample'
          }.`}
          link="/projects/SCPCP000006"
          linkLabel=" Inspect"
          newTab
        />
      )}
    </>
  )
}

export default WarningSpatialSamples
