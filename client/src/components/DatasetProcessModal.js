import React, { useEffect, useState } from 'react'
import { Box, Grid, Paragraph } from 'grommet'
import { useRouter } from 'next/router'
import { useMyDataset } from 'hooks/useMyDataset'
import { Button } from 'components/Button'
import { DatasetProcessForm } from 'components/DatasetProcessForm'
import { Modal, ModalBody } from 'components/Modal'

// Button and modal to show when initiating dataset processing for file download
export const DatasetProcessModal = ({
  label = 'Download Dataset',
  title = 'Download Dataset',
  disabled = false,
  onRedirecting = () => {}
}) => {
  const { push } = useRouter()
  const { processMyDataset } = useMyDataset()

  const [showing, setShowing] = useState(false)
  const [submitting, setSubmitting] = useState(false) // Disable the button while making request

  useEffect(() => {
    const submit = async () => {
      const datasetRequest = await processMyDataset()
      if (datasetRequest) {
        onRedirecting(true)
        push(`/datasets/${datasetRequest.id}`)
      } else {
        // TODO: Error handling
        setSubmitting(false)
        setShowing(false)
      }
    }

    if (submitting) submit()
  }, [submitting])

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        primary
        label={label}
        disabled={disabled}
        onClick={() => setShowing(true)}
      />
      <Modal title={title} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
            <Box pad={{ bottom: 'large' }} gap="medium" width="500px">
              <Paragraph>
                We’re getting ready to put your dataset together. This can take
                between a few hours to a day.
              </Paragraph>
              <DatasetProcessForm
                buttonLabel="Continue"
                onCancel={() => setShowing(false)}
                onContinue={() => setSubmitting(true)}
              />
            </Box>
          </Grid>
        </ModalBody>
      </Modal>
    </>
  )
}

export default DatasetProcessModal
