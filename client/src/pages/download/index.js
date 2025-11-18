import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useMyDataset } from 'hooks/useMyDataset'
import { useResponsive } from 'hooks/useResponsive'
import { useNotification } from 'hooks/useNotification'
import { formatBytes } from 'helpers/formatBytes'
import { getReadable } from 'helpers/getReadable'
import { DatasetEmpty } from 'components/DatasetEmpty'
import { DatasetSummary } from 'components/DatasetSummary'
import { DatasetDownloadFileSummary } from 'components/DatasetDownloadFileSummary'
import { DatasetProjectSummary } from 'components/DatasetProjectSummary'
import { DatasetProcessModal } from 'components/DatasetProcessModal'
import { InfoText } from 'components/InfoText'
import { Loader } from 'components/Loader'
import Error from 'pages/_error'

const Download = () => {
  const { restoreScrollPosition } = useScrollRestore()
  const {
    myDataset,
    myDatasetFormat,
    setMyDatasetFormat,
    errors,
    getDataset,
    isDatasetDataEmpty
  } = useMyDataset()
  const { responsive } = useResponsive()

  const [loading, setLoading] = useState(true)
  const [isFormatChanged, setIsFormatChanged] = useState(false)

  const { hideNotification } = useNotification()
  // Clean up the moved samples banner on component unmounts
  useEffect(() => {
    const bannerName = 'Move to My Dataset' // A moved samples banner ID
    return () => {
      hideNotification(bannerName)
    }
  }, [])

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

  // Display a message if the format has changed
  useEffect(() => {
    if (myDataset.format !== myDatasetFormat) {
      setIsFormatChanged(true)
      setMyDatasetFormat(myDataset.format)
    }
  }, [loading])

  if (loading) return <Loader />

  // TODO: Replace this once error handling is finalized
  // Show error page if there are any API errors
  if (errors.length > 0) return <Error />

  return (
    <Box width="full" pad={responsive({ horizontal: 'medium' })}>
      {isDatasetDataEmpty ? (
        <DatasetEmpty />
      ) : (
        <>
          <Box direction="row" justify="between" pad={{ bottom: 'large' }}>
            <Box>
              <Text serif size="xlarge">
                My Dataset
              </Text>
              {isFormatChanged && (
                <InfoText>
                  <Text>
                    The data format has changed to{' '}
                    {getReadable(myDataset.format)}
                  </Text>
                </InfoText>
              )}
            </Box>
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
