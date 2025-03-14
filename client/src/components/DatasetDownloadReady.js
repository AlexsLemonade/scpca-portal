import React from 'react'
import { Box, Paragraph, Text } from 'grommet'

// View when the user has token in local storage
export const DatasetDownloadReady = () => {
  // NOTE: We use ScPCAPortalContext or a new context for Dataset for managing email
  const email = 'myemail@example.com'

  return (
    <Box>
      <Paragraph margin={{ bottom: 'small' }}>
        We’ll send a email to <Text weight="bold">{email}</Text> once the
        dataset is ready to be downloaded.
      </Paragraph>
    </Box>
  )
}

export default DatasetDownloadReady
