import React from 'react'
import { Box } from 'grommet'
import { DatasetHeroExpired } from 'components/DatasetHeroExpired'
import { DatasetHeroProcessing } from 'components/DatasetHeroProcessing'
import { DatasetHeroReady } from 'components/DatasetHeroReady'

// NOTE: This component accepts 'dataset' prop but it's subject to change
// Currently mock data is used via Storybook for development
export const DatasetHero = ({
  dataset,
  isToken = false // temporary for Storybook
}) => {
  // NOTE: Addd a helper to map the API dataset state and the correponding components
  const {
    is_errored: isError,
    is_expired: isExpired,
    is_processing: isProcessing,
    is_processed: isProcessed
  } = dataset
  // These variables are temporary
  const isDownloadReady = !isError && !isExpired && isProcessed
  const isDownloadExpired = !isError && isExpired && isProcessed

  return (
    <Box
      justify="center"
      border={{ side: 'bottom', size: 'small' }}
      margin={{ bottom: 'xlarge' }}
      pad={{ bottom: 'xlarge' }}
    >
      {isDownloadExpired && <DatasetHeroExpired />}
      {isProcessing && <DatasetHeroProcessing />}
      {isDownloadReady && <DatasetHeroReady isToken={isToken} />}
    </Box>
  )
}

export default DatasetHero
