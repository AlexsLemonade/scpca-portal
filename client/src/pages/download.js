import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { DatasetSummary } from 'components/DatasetSummary'
import { DatasetDownloadFileSummary } from 'components/DatasetDownloadFileSummary'
import { DatasetProjectCard } from 'components/DatasetProjectCard'
import { Loader } from 'components/Loader'
import Error from 'pages/_error'

const Download = () => {
  const { myDataset, errors, getDataset, hasDatasetData } = useDatasetManager()
  const { responsive } = useResponsive()

  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDataset = async () => {
      await getDataset()
      setLoading(false)
    }

    fetchDataset()
  }, [])

  if (loading) return <Loader />

  // TODO: Replace this once error handling is finalized
  // Show error page if there are any API errors
  if (errors.length > 0) return <Error />

  return (
    <Box width="full" pad={responsive({ horizontal: 'medium' })}>
      {hasDatasetData() ? (
        <Box>Dataset is empty</Box> // TODO: Replace the temporary JSX with Deepa's mockup
      ) : (
        <>
          <Box direction="row" justify="between" pad={{ bottom: 'large' }}>
            <Text serif size="xlarge">
              My Dataset
            </Text>
          </Box>
          <Box margin={{ bottom: 'large' }}>
            <DatasetSummary dataset={myDataset} />
          </Box>
          <Box margin={{ bottom: 'large' }}>
            <DatasetDownloadFileSummary dataset={myDataset} />
          </Box>
          <Box margin={{ bottom: 'large' }}>
            {Object.keys(myDataset.data).map((p) => (
              <Box margin={{ bottom: 'large' }}>
                <DatasetProjectCard key={p} dataset={myDataset} projectId={p} />
              </Box>
            ))}
          </Box>
        </>
      )}
    </Box>
  )
}

export default Download
