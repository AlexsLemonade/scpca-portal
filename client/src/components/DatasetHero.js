import React, { useEffect, useState } from 'react'
import { Box } from 'grommet'
import { useDataset } from 'hooks/useDataset'
import { DatasetHeroExpired } from 'components/DatasetHeroExpired'
import { DatasetHeroProcessing } from 'components/DatasetHeroProcessing'
import { DatasetHeroReady } from 'components/DatasetHeroReady'
import { DatasetResourceLinks } from 'components/DatasetResourceLinks'
import { Loader } from 'components/Loader'

export const DatasetHero = ({ dataset }) => {
  const { getDatasetState } = useDataset()
  const { isProcessing, isReady, isExpired } = getDatasetState(dataset)

  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(false)
  }, [])

  if (loading) return <Loader />

  return (
    <>
      {(isExpired || isProcessing || isReady) && (
        <Box
          justify="center"
          border={{ side: 'bottom', color: 'border-black', size: 'small' }}
          margin={{ bottom: 'xlarge' }}
          pad={{ bottom: 'xlarge' }}
        >
          {isExpired && <DatasetHeroExpired dataset={dataset} />}
          {isProcessing && <DatasetHeroProcessing />}
          {isReady && <DatasetHeroReady dataset={dataset} />}
        </Box>
      )}
      {(isProcessing || isReady) && (
        <Box
          justify="center"
          border={{ side: 'bottom', color: 'border-black', size: 'small' }}
          margin={{ bottom: 'xlarge' }}
          pad={{ bottom: 'xlarge' }}
        >
          <DatasetResourceLinks />
        </Box>
      )}
    </>
  )
}

export default DatasetHero
