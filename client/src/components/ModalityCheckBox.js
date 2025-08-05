import React from 'react'
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

export const ModalityCheckBox = ({ modality, sampleId, disabled, onClick }) => {
  const { myDataset, userFormat } = useDatasetManager()
  const { selectedSamples } = useDatasetSamplesTable()

  const disableSpatial =
    modality === 'SPATIAL' && (myDataset.format || userFormat) === 'ANN_DATA'

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
