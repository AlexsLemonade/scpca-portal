import React, { useEffect, useRef, useState } from 'react'
import { Box } from 'grommet'
import { api } from 'api'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useDataset } from 'hooks/useDataset'
import { useMyDataset } from 'hooks/useMyDataset'
import { useResponsive } from 'hooks/useResponsive'
import { useRouter } from 'next/router'
import { DatasetMoveSamplesModal } from 'components/DatasetMoveSamplesModal'
import { DatasetHero } from 'components/DatasetHero'
import { DatasetSummary } from 'components/DatasetSummary'
import { DatasetDownloadFileSummary } from 'components/DatasetDownloadFileSummary'
import { DatasetProjectSummary } from 'components/DatasetProjectSummary'

const Dataset = ({ dataset: initialDataset }) => {
  const { restoreScrollPosition } = useScrollRestore()
  const { responsive } = useResponsive()
  const { get, getDatasetState } = useDataset()
  const { myDataset } = useMyDataset()
  const { push } = useRouter()

  const pollTimer = useRef(null)
  const pollInterval = 1000 * 60
  const [dataset, setDataset] = useState(initialDataset)

  const { isProcessing } = getDatasetState(dataset)

  // Restore scroll position after component mounts
  useEffect(() => {
    restoreScrollPosition()
  }, [])

  // Add safeguard to prevent users from accessing active dataset
  useEffect(() => {
    if (dataset.id === myDataset.id) {
      push(`/download`)
    }
  }, [dataset, myDataset])

  // Poll API during dataset processing
  // TODO: Generalize this logic into a hook
  useEffect(() => {
    const pollDataset = async () => {
      const datasetRequest = await get(dataset)
      setDataset(datasetRequest)
      // stop polling when done
      if (!datasetRequest.is_processing) {
        clearInterval(pollTimer.current)
      }
    }

    // Initiate polling the dataset status
    if (isProcessing) {
      pollTimer.current = setInterval(pollDataset, pollInterval)
    }

    return () => clearInterval(pollTimer.current)
  }, [])

  return (
    <>
      <Box pad={{ top: responsive('medium', 'xlarge') }} fill>
        <DatasetHero dataset={dataset} />
      </Box>
      <Box pad={responsive({ horizontal: 'medium' })} fill>
        <Box margin={{ bottom: 'large' }}>
          <DatasetSummary dataset={dataset}>
            <DatasetMoveSamplesModal dataset={dataset} />
          </DatasetSummary>
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
