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

  const disableSpatial =
    modality === 'SPATIAL' && myDataset?.format === 'ANN_DATA'

  // Preselect any samples that are in myDataset
  useEffect(() => {
    const projectData = getProjectData(project)
    const singleCellSamples = projectData?.SINGLE_CELL
    const spatialSamples = projectData?.SPATIAL

    if (singleCellSamples) {
      selectModalitySamplesByIds('SINGLE_CELL', singleCellSamples)
    }

    if (spatialSamples) {
      selectModalitySamplesByIds('SPATIAL', spatialSamples)
    }
  }, [myDataset, allSamples])

  return (
    <CheckBox
      name={modality}
      checked={!disabled ? selectedSamples[modality].includes(sampleId) : false}
      disabled={disabled || disableSpatial}
      onClick={onClick}
    />
  )
}

export default ModalityCheckBox
