import React, { useEffect } from 'react'
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
  sampleId,
  disabled,
  onClick
}) => {
  const { myDataset, getProjectData } = useDatasetManager()
  const { allSamples, selectedSamples, selectModalitySamplesByIds } =
    useDatasetSamplesTable()

  // Preselect any samples that are in myDataset
  useEffect(() => {
    const { SINGLE_CELL: singleCellSamples, SPATIAL: spatialSamples } =
      getProjectData(project)

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

  return (
    <CheckBox
      name={modality}
      checked={!disabled ? selectedSamples[modality].includes(sampleId) : false}
      disabled={disabled}
      onClick={onClick}
    />
  )
}

export default ModalityCheckBox
