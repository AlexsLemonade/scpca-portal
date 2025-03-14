import React, { useEffect, useState } from 'react'
import { Box, Grid, Paragraph } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { DatasetDownloadReady } from 'components/DatasetDownloadReady'
import { DatasetDownloadToken } from 'components/DatasetDownloadToken'

import { Modal, ModalBody } from 'components/Modal'

// Button and modal to show when starting dataset processing for file download
export const DatasetDownloadModal = ({
  label = 'Download Dataset',
  title = 'Download Dataset',
  disabled = false,
  isToken = false // temporary
}) => {
  const { responsive } = useResponsive()
  // NOTE: We use ScPCAPortalContext or a new context for Dataset for managing token
  const [token, setToken] = useState(isToken)
  const [showing, setShowing] = useState(false)

  const handleClick = () => {
    setShowing(true)
  }

  // temporary
  // NOTE: We handle the token generation in DatasetDownloadToken
  useEffect(() => {
    setToken(isToken)
  }, [isToken])

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        primary
        label={label}
        disabled={disabled}
        onClick={handleClick}
      />
      <Modal title={title} showing={showing} setShowing={setShowing}>
        <ModalBody>
          <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
            <Box pad={{ bottom: 'large' }} width="500px">
              <Paragraph margin={{ bottom: '0' }}>
                We’re getting ready to put your dataset together. This can take
                between a few hours to a day.
              </Paragraph>
              {token ? <DatasetDownloadReady /> : <DatasetDownloadToken />}
            </Box>
            <Box
              align="center"
              justify="end"
              direction={responsive('column', 'row')}
              gap="medium"
            >
              <Button
                aria-label="Cancel"
                label="Cancel"
                onClick={() => setShowing(false)}
              />
              <Button primary aria-label="Continue" label="Continue" />
            </Box>
          </Grid>
        </ModalBody>
      </Modal>
    </>
  )
}

export default DatasetDownloadModal
