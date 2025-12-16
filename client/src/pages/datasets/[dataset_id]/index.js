import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { api } from 'api'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useDataset } from 'hooks/useDataset'
import { useResponsive } from 'hooks/useResponsive'
import { DatasetMoveSamplesModal } from 'components/DatasetMoveSamplesModal'
import { DatasetHero } from 'components/DatasetHero'
import { DatasetSummary } from 'components/DatasetSummary'
import { DatasetDownloadFileSummary } from 'components/DatasetDownloadFileSummary'
import { DatasetProjectSummary } from 'components/DatasetProjectSummary'

const Dataset = ({ dataset: initialDataset }) => {
  const { restoreScrollPosition } = useScrollRestore()
  const { responsive } = useResponsive()
  const { get, getDatasetState } = useDataset()

  const { isProcessing, isUnprocessed } = getDatasetState(initialDataset)

  const [dataset, setDataset] = useState(initialDataset)

  // Restore scroll position after component mounts
  useEffect(() => {
    restoreScrollPosition()
  }, [])

  // TODO: We're temporarily polling in this component
  // Poll API when during dataset processing
  useEffect(() => {
    let pollRequest

    if (isProcessing) {
      pollRequest = setInterval(async () => {
        const datasetRequest = await get(dataset)
        setDataset(datasetRequest)
      }, 1000 * 60)
    }

    return () => {
      if (pollRequest) {
        clearInterval(pollRequest)
      }
    }
  }, [isProcessing, dataset])

  return (
    <>
      <Box pad={{ top: responsive('medium', 'xlarge') }} fill>
        <DatasetHero dataset={dataset} />
      </Box>
      <Box pad={responsive({ horizontal: 'medium' })} fill>
        <Box
          direction="row"
          justify={isUnprocessed ? 'between' : 'end'}
          pad={{ bottom: 'large' }}
          fill
        >
          {isUnprocessed && (
            <Text serif size="xlarge">
              Shared Dataset
            </Text>
          )}
          <Box>
            <DatasetMoveSamplesModal dataset={dataset} />
          </Box>
        </Box>
        <Box margin={{ bottom: 'large' }}>
          <DatasetSummary dataset={dataset} />
        </Box>
        <Box margin={{ bottom: 'large' }}>
          <DatasetDownloadFileSummary dataset={dataset} />
        </Box>
        <Box margin={{ bottom: 'large' }}>
          <DatasetProjectSummary dataset={dataset} readOnly />
        </Box>
      </Box>
    </>
  )
}

export const getServerSideProps = async ({ query }) => {
  const datasetRequest = await api.datasets.get(query.dataset_id)

  if (datasetRequest.isOk) {
    const dataset = datasetRequest.response
    return {
      props: { dataset }
    }
  }

  if (datasetRequest.status === 404) {
    return { notFound: true }
  }

  return { props: { dataset: null } }
}

export default Dataset
