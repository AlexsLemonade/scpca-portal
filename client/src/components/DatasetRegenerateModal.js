import React, { useState } from 'react'
import { Box, Grid, Paragraph } from 'grommet'
import { useRouter } from 'next/router'
import { useDataset } from 'hooks/useDataset'
import { Button } from 'components/Button'
import { DatasetProcessForm } from 'components/DatasetProcessForm'
import { Modal, ModalBody } from 'components/Modal'

// Button and modal to show when regenerating dataset processing for file download
export const DatasetRegenerateModal = ({
  dataset,
  label = 'Regenerate Dataset',
  title = 'Regenerate Dataset',
  disabled = false
}) => {
  const { push } = useRouter()
  const { regenerate } = useDataset()

  const [showing, setShowing] = useState(false)

  const handleRegenerateDataset = async () => {
    const datasetRequest = await regenerate(dataset)

    if (datasetRequest) {
      push(`/datasets/${datasetRequest.id}`)
      setShowing(false)
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
                onCancel={() => setShowing(false)}
                onContinue={handleRegenerateDataset}
              />
            </Box>
          </Grid>
        </ModalBody>
      </Modal>
    </>
  )
}

export default DatasetRegenerateModal
