import React from 'react'
import { Box, Paragraph, Text } from 'grommet'

// View when the user has token in local storage
export const DatasetDownloadReady = () => {
  return (
    <Box>
      <Paragraph margin={{ bottom: 'small' }}>
        We’ll send a email to{' '}
        <Text weight="bold">myemail@emailservice.com</Text> once the dataset is
        ready to be downloaded.
      </Paragraph>
    </Box>
  )
}

export default DatasetDownloadReady
