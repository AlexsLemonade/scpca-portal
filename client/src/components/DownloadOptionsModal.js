import { Box, Button, FormField, Select, Text } from 'grommet'
import { Modal, ModalBody } from 'components/Modal'
import { HelpLink } from 'components/HelpLink'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'
import getReadableOptions from 'helpers/getReadableOptions'
import config from 'config'
import styled from 'styled-components'

const BlueButton = styled(Button)`
   color: ${({ theme }) => theme.global.colors.brand.light};
`

export const DownloadOptionsModal = ({
  label = "Change",
  title = "Set Download Options",
  showing = false,
  setShowing = () => { },
  onSave = () => { }
}) => {

  const {
    modalityOptions,
    formatOptions,
    selectedModality,
    setSelectedModality,
    selectedFormat,
    setSelectedFormat,
    applySelection
  } = useDownloadOptionsContext()

  const handleOptionsSave = () => {
    applySelection()
    onSave()
  }

  return (
    <>
      <BlueButton
        label={label}
        plain
        color="brand"
        onClick={() => setShowing(!showing)}
      />
      <Modal
        title={title}
        showing={showing}
        setShowing={setShowing}>
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
                  valueKey={{ key: "value", reduce: true }}
                  value={selectedModality}
                  onChange={({ value }) => setSelectedModality(value)}
                />
              </FormField>
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
                  valueKey={{ key: "value", reduce: true }}
                  value={selectedFormat}
                  onChange={({ value }) => setSelectedFormat(value)}
                />
              </FormField>
            </Box>
            <Box direction="row" gap="medium" justify="end">
              <Button label="Cancel" onClick={() => setShowing(false)} />
              <Button
                label="Save"
                primary
                onClick={handleOptionsSave}
              />
            </Box>
          </Box>
        </ModalBody>
      </Modal >
    </>
  )
}

export default DownloadOptionsModal
