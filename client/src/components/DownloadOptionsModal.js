import React, { useEffect, useState } from 'react'
import { Box, Button, FormField, Select, Text } from 'grommet'
import { Modal, ModalBody } from 'components/Modal'
import { HelpLink } from 'components/HelpLink'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'
import getReadableOptions from 'helpers/getReadableOptions'
import filterWhere from 'helpers/filterWhere'
import config from 'config'
import styled from 'styled-components'

const BlueButton = styled(Button)`
  color: ${({ theme }) => theme.global.colors.brand.light};
`

export const DownloadOptionsModal = ({
  label = 'Change',
  title = 'Set Download Options',
  showing = false,
  setShowing = () => {},
  onSave = () => {}
}) => {
  const {
    computedFiles,
    format,
    formatOptions,
    modality,
    modalityOptions,
    getOptionsAndDefault,
    saveUserPreferences
  } = useDownloadOptionsContext()

  // allow user to change before updating
  const [selectedModality, setSelectedModality] = useState(modality)
  const [selectedFormat, setSelectedFormat] = useState(format)
  const [selectedFormatOptions, setSelectedFormatOptions] =
    useState(formatOptions)

  const handleOptionsSave = () => {
    saveUserPreferences(selectedModality, selectedFormat)
    onSave()
  }

  // Reset drop-down values to user preference on cancel
  useEffect(() => {
    if (!showing) {
      setSelectedFormat(format)
      setSelectedModality(modality)
    }
  }, [showing])

  // Update available data format options locally when a user changes modality (i.e. selectedModality) via drop-down
  useEffect(() => {
    if (!selectedModality) return

    const modalityMatchedFiles = filterWhere(computedFiles, {
      modality: selectedModality
    })

    const [newFormatOptions, newFormat] = getOptionsAndDefault(
      'format',
      selectedFormat,
      modalityMatchedFiles
    )
    setSelectedFormatOptions(newFormatOptions)
    // Only assign format when unset
    setSelectedFormat(newFormat)
  }, [selectedModality])

  return (
    <>
      <BlueButton
        label={label}
        plain
        color="brand"
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
              <FormField label="Modality">
                <Select
                  options={getReadableOptions(modalityOptions)}
                  labelKey="label"
                  valueKey={{ key: 'value', reduce: true }}
                  value={selectedModality}
                  onChange={({ value }) => setSelectedModality(value)}
                />
              </FormField>
              <FormField
                label={
                  <HelpLink
                    label="Data Format"
                    link={config.links.whatDownloading}
                  />
                }
              >
                <Select
                  options={getReadableOptions(selectedFormatOptions)}
                  labelKey="label"
                  valueKey={{ key: 'value', reduce: true }}
                  value={selectedFormat}
                  onChange={({ value }) => setSelectedFormat(value)}
                />
              </FormField>
            </Box>
            <Box direction="row" gap="medium" justify="end">
              <Button label="Cancel" onClick={() => setShowing(false)} />
              <Button label="Save" primary onClick={handleOptionsSave} />
            </Box>
          </Box>
        </ModalBody>
      </Modal>
    </>
  )
}

export default DownloadOptionsModal
