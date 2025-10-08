import React, { useState } from 'react'
import { Box, RadioButtonGroup, Text } from 'grommet'
import { useRouter } from 'next/router'
import { useMyDataset } from 'hooks/useMyDataset'
import { useNotification } from 'hooks/useNotification'
import { useResponsive } from 'hooks/useResponsive'
import { config } from 'config'
import { Button } from 'components/Button'
import { Modal, ModalBody } from 'components/Modal'
import { WarningText } from 'components/WarningText'
import { InfoText } from 'components/InfoText'
import { Link } from 'components/Link'
import { FormField } from 'components/FormField'

export const DatasetMoveSamplesModal = ({
  dataset,
  label = 'Move to My Dataset',
  title = 'Move Samples to My Dataset',
  disabled = false
}) => {
  const { push } = useRouter()
  const {
    myDataset,
    clearDataset,
    createDataset,
    mergeDatasetData,
    updateDataset
  } = useMyDataset()
  const { showNotification } = useNotification()
  const { responsive } = useResponsive()

  const [showing, setShowing] = useState(false)

  // Show only the replace action if the formats are different
  const isFormatChanged = myDataset.id && myDataset.format !== dataset.format

  const radioOptions = [
    {
      label: 'Append samples to My Dataset',
      value: 'append',
      disabled: isFormatChanged
    },
    { label: 'Replace My Dataset', value: 'replace' }
  ]
  const defaultAction = isFormatChanged
    ? radioOptions[1].value
    : radioOptions[0].value
  const [action, setAction] = useState(defaultAction)

  const { total_sample_count: initialSampleCount } = myDataset
  const { total_sample_count: sharedSampleCount } = dataset

  const showErrorNotification = (
    message = "We're having trouble moving samples to My Dataset. Please try again later."
  ) => {
    showNotification(message, 'error')
    setShowing(false)
  }

  const handleMoveToMyDataset = async () => {
    const updatedData =
      action === 'append'
        ? await mergeDatasetData(dataset)
        : structuredClone(dataset.data)

    // API failure while merging data
    if (!updatedData) {
      showErrorNotification()
      return
    }

    // Clear the data in My Dataset if the format has changed
    if (isFormatChanged) await clearDataset()

    const updatedDataset = !myDataset.id
      ? await createDataset({ format: dataset.format, data: updatedData })
      : await updateDataset({
          ...myDataset,
          format: dataset.format,
          data: updatedData
        })

    // API failure while updating the dataset
    if (!updatedDataset) {
      showErrorNotification()
      return
    }

    push(`/download`)
    showNotification(`Moved ${sharedSampleCount} Samples to My Dataset`)
    setShowing(false)
  }

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        label={label}
        disabled={disabled}
        onClick={() => setShowing(true)}
      />
      <Modal title={title} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <WarningText
            lineBreak={false}
            iconMargin="0"
            iconSize="24px"
            margin={{ bottom: 'medium' }}
          >
            <Text size="21px" margin={{ left: 'xsmall' }}>
              There are {initialSampleCount} samples in My Dataset
            </Text>
          </WarningText>
          <FormField>
            <RadioButtonGroup
              name="action"
              options={radioOptions}
              value={action}
              onChange={({ target: { value } }) => setAction(value)}
            />
          </FormField>
          <Box margin={{ top: 'medium' }} width={{ max: '440px' }}>
            {!isFormatChanged && (
              <InfoText iconSize="24px">
                <Text margin={{ left: 'small' }}>
                  Some download options may have changed. Please review the
                  dataset before you download.{' '}
                  <Link
                    href={config.links.what_review_dataset}
                    label="Learn more"
                  />
                </Text>
              </InfoText>
            )}
          </Box>
          <Box
            align="center"
            direction={responsive('column', 'row')}
            gap="xlarge"
            justify="end"
            margin={{ top: 'large' }}
          >
            <Button
              primary
              aria-label="Move Samples"
              label="Move Samples"
              onClick={handleMoveToMyDataset}
            />
          </Box>
        </ModalBody>
      </Modal>
    </>
  )
}
