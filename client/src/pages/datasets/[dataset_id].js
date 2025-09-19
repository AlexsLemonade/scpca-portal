import React, { useEffect } from 'react'
import { Box } from 'grommet'
import { api } from 'api'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useDataset } from 'hooks/useDataset'
import { useResponsive } from 'hooks/useResponsive'
import { DatasetSummary } from 'components/DatasetSummary'
import { DatasetDownloadFileSummary } from 'components/DatasetDownloadFileSummary'
import { DatasetProjectCard } from 'components/DatasetProjectCard'
import Error from 'pages/_error'

const Dataset = ({ dataset }) => {
  const { restoreScrollPosition } = useScrollRestore()
  const { errors } = useDataset()
  const { responsive } = useResponsive()

  // Restore scroll position after component mounts
  useEffect(() => {
    restoreScrollPosition()
  }, [])

  // TODO: Replace this once error handling is finalized
  // Show error page if there are any API errors
  if (errors.length > 0) return <Error />

  return (
    <Box width="full" pad={responsive({ horizontal: 'medium' })}>
      <Box alignSelf="end">
        {/* // TODO: Move to Dataset button will be added in issue #1410 */}
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
