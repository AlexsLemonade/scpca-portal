import React, { useEffect, useState } from 'react'
import { CheckBox as GrommetCheckBox } from 'grommet'
import styled, { css } from 'styled-components'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'

const CheckBox = styled(GrommetCheckBox)`
  + div {
    width: 24px;
    height: 24px;
  }
  ${({ theme }) => css`
    &:not(:checked) {
      + div {
        background: ${theme.global.colors.white};
      }
    }
  `}
`

export const ModalityCheckBox = ({
  project,
  modality,
  samples,
  sampleId,
  disabled,
  onClick
}) => {
  const { myDataset, getDatasetData, getProjectSingleCellSamples } =
    useDatasetManager()
  const { allSamples, selectedSamples, selectModalitySamplesByIds } =
    useDatasetSamplesTable()

  const [isAlreadyInMyDataset, setIsAlreadyInMyDataset] = useState(false)

  const datasetData = getDatasetData(project)

  // Preselect samples that are already in myDataset
  useEffect(() => {
    const { SINGLE_CELL: singleCellSamples, SPATIAL: spatialSamples } =
      datasetData
    if (singleCellSamples) {
      // If the project is a merged object, add all SINGLE_CELL samples
      const samplesToSelect =
        singleCellSamples === 'MERGED'
          ? allSamples
              .filter((s) => s.has_single_cell_data)
              .map((s) => s.scpca_id)
          : singleCellSamples

      selectModalitySamplesByIds('SINGLE_CELL', samplesToSelect)
    }

    if (spatialSamples) {
      selectModalitySamplesByIds('SPATIAL', spatialSamples)
    }
  }, [myDataset, allSamples])

  // Disable samples that are already in myDataset
  useEffect(() => {
    if (samples) {
      const datasetSamplesByModality = {
        SINGLE_CELL:
          datasetData.SINGLE_CELL === 'MERGED'
            ? getProjectSingleCellSamples(samples)
            : datasetData.SINGLE_CELL || [],
        SPATIAL: datasetData.SPATIAL || []
      }

      setIsAlreadyInMyDataset(
        datasetSamplesByModality[modality].includes(sampleId)
      )
    }
  }, [myDataset, samples])

  return (
    <CheckBox
      name={modality}
      checked={!disabled ? selectedSamples[modality].includes(sampleId) : false}
      disabled={disabled || isAlreadyInMyDataset}
      onClick={onClick}
    />
  )
}

export default ModalityCheckBox
