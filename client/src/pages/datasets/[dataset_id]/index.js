import React, { useEffect } from 'react'
import { Box, Text } from 'grommet'
import { api } from 'api'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useDataset } from 'hooks/useDataset'
import { useResponsive } from 'hooks/useResponsive'
import { DatasetMoveSamplesModal } from 'components/DatasetMoveSamplesModal'
import { DatasetSummary } from 'components/DatasetSummary'
import { DatasetDownloadFileSummary } from 'components/DatasetDownloadFileSummary'
import { DatasetProjectCard } from 'components/DatasetProjectCard'

const Dataset = ({ dataset }) => {
  const { restoreScrollPosition } = useScrollRestore()
  const { responsive } = useResponsive()
  const { getDatasetState } = useDataset()

  const { isUnprocessed } = getDatasetState(dataset)

  // Restore scroll position after component mounts
  useEffect(() => {
    restoreScrollPosition()
  }, [])

  return (
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
        {Object.keys(dataset.data)
          .sort()
          .map((pId) => (
            <Box margin={{ bottom: 'large' }} key={pId}>
              <DatasetProjectCard dataset={dataset} projectId={pId} readOnly />
            </Box>
          ))}
      </Box>
    </Box>
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
