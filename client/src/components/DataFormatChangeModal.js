import React, { useEffect, useState } from 'react'
import { Box, Button, FormField, Select, Text } from 'grommet'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { HelpLink } from 'components/HelpLink'
import { Modal, ModalBody } from 'components/Modal'
import { getReadableOptions } from 'helpers/getReadableOptions'
import { config } from 'config'
import styled, { css } from 'styled-components'

// TODO: Temporarily disable Change button until format flow is finalized
const BlueButton = styled(Button)`
  ${({ theme, disabled }) => css`
    color: ${disabled
      ? theme.global.colors['black-tint-60']
      : theme.global.colors.brand.light};
    cursor: ${disabled ? 'not-allowed' : 'pointer'};
  `}
`

export const DataFormatChangeModal = ({
  label = 'Change',
  title = 'Set Data Format',
  project,
  disabled,
  showing = false,
  setShowing = () => {}
}) => {
  const { userFormat, setUserFormat } = useScPCAPortal()

  const formatOptions = [
    { key: 'SINGLE_CELL_EXPERIMENT', value: project.has_single_cell_data },
    { key: 'ANN_DATA', value: project.includes_anndata }
  ]
    .filter((f) => f.value)
    .map((f) => f.key)
  const defaultFormat = formatOptions.includes(userFormat)
    ? userFormat
    : formatOptions[0]

  const [format, setFormat] = useState(defaultFormat)

  const handleChange = (value) => {
    setFormat(value)
  }

  const handleSave = () => {
    setUserFormat(format)
    setShowing(false)
  }

  // Reset form on cancel
  useEffect(() => {
    if (!showing) {
      setFormat(userFormat)
    }
  }, [showing])

  return (
    <>
      <BlueButton
        label={label}
        plain
        color="brand"
        disabled={disabled}
        onClick={() => setShowing(!showing)}
      />
      <Modal title={title} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <Text>
            These options will be applied to all the samples in this project
          </Text>
          <Box>
            <Box
              direction="row"
              alignContent="between"
              gap="large"
              pad={{ bottom: 'large' }}
            >
              <FormField
                label={
                  <HelpLink
                    label="Data Format"
                    link={config.links.what_downloading}
                  />
                }
              >
                <Select
                  options={getReadableOptions(formatOptions)}
                  labelKey="label"
                  valueKey={{ key: 'value', reduce: true }}
                  value={format}
                  onChange={({ value }) => handleChange(value)}
                />
              </FormField>
            </Box>
            <Box direction="row" gap="medium" justify="end">
              <Button label="Cancel" onClick={() => setShowing(false)} />
              <Button label="Save" primary onClick={handleSave} />
            </Box>
          </Box>
        </ModalBody>
      </Modal>
    </>
  )
}

export default DataFormatChangeModal
