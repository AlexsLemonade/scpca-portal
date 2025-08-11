import React from 'react'
import { CheckBox as GrommetCheckBox } from 'grommet'
import styled, { css } from 'styled-components'
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
  const { selectedSamples } = useDatasetSamplesTable()

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
