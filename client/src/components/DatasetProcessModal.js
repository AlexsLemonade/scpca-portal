import React, { useState } from 'react'
import { Box, Grid, Paragraph } from 'grommet'
import { useRouter } from 'next/router'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { Button } from 'components/Button'
import { DatasetProcessForm } from 'components/DatasetProcessForm'
import { Modal, ModalBody } from 'components/Modal'

// Button and modal to show when initiating dataset processing for file download
export const DatasetProcessModal = ({
  label = 'Download Dataset',
  title = 'Download Dataset',
  disabled = false
}) => {
  const { push } = useRouter()
  const { processDataset } = useDatasetManager()

  const [showing, setShowing] = useState(false)

  const handleProcessDataset = async () => {
    const datasetRequest = await processDataset()

    if (datasetRequest) {
      push(`/datasets/${datasetRequest.id}`)
    } else {
      // TODO: Error handling
    }
  }

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
                onContinue={handleProcessDataset}
              />
            </Box>
          </Grid>
        </ModalBody>
      </Modal>
    </>
  )
}

export default DatasetProcessModal
