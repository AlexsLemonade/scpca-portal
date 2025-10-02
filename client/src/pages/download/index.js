import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useMyDataset } from 'hooks/useMyDataset'
import { useResponsive } from 'hooks/useResponsive'
import { formatBytes } from 'helpers/formatBytes'
import { DatasetSummary } from 'components/DatasetSummary'
import { DatasetDownloadFileSummary } from 'components/DatasetDownloadFileSummary'
import { DatasetProjectSummary } from 'components/DatasetProjectSummary'
import { DatasetProcessModal } from 'components/DatasetProcessModal'
import { Loader } from 'components/Loader'
import Error from 'pages/_error'

const Download = () => {
  const { restoreScrollPosition } = useScrollRestore()
  const { myDataset, errors, getDataset, isDatasetDataEmpty } = useMyDataset()
  const { responsive } = useResponsive()

  const [loading, setLoading] = useState(true)

  // Restore scroll position after component mounts
  useEffect(() => {
    if (!loading) {
      restoreScrollPosition()
    }
  }, [loading])

  useEffect(() => {
    const fetchDataset = async () => {
      await getDataset()
      setLoading(false)
    }

    if (loading) fetchDataset()
  }, [loading, myDataset])

  if (loading) return <Loader />

  // TODO: Replace this once error handling is finalized
  // Show error page if there are any API errors
  if (errors.length > 0) return <Error />

  return (
    <Box width="full" pad={responsive({ horizontal: 'medium' })}>
      {isDatasetDataEmpty ? (
        <Box>Dataset is empty</Box> // TODO: Replace the temporary JSX with Deepa's mockup
      ) : (
        <>
          <Box direction="row" justify="between" pad={{ bottom: 'large' }}>
            <Text serif size="xlarge">
              My Dataset
            </Text>
            <Box>
              <DatasetProcessModal />
              <Text weight="bold">
                Uncompressed size:{' '}
                {formatBytes(myDataset.estimated_size_in_bytes)}
              </Text>
            </Box>
          </Box>
          <Box margin={{ bottom: 'large' }}>
            <DatasetSummary dataset={myDataset} />
          </Box>
          <Box margin={{ bottom: 'large' }}>
            <DatasetDownloadFileSummary dataset={myDataset} />
          </Box>
          <Box margin={{ bottom: 'large' }}>
            <DatasetProjectSummary dataset={myDataset} />
          </Box>
        </>
      )}
    </Box>
  )
}

export default Download
