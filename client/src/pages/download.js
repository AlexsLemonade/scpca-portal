import React, { useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { Loader } from 'components/Loader'
import Error from 'pages/_error'

const Download = () => {
  const { myDataset, errors, getDataset } = useDatasetManager()
  const { responsive } = useResponsive()

  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDataset = async () => {
      if (myDataset.id) {
        await getDataset()
      }
      setLoading(false)
      // TODO: Remove temporary log after completing integration
      // eslint-disable-next-line no-console
      console.log({ myDataset })
    }

    fetchDataset()
  }, [myDataset.id])

  if (loading) return <Loader />

  // TODO: Replace this once error handling is finalized
  // Show error page if there are any API errors
  if (errors.length > 0) return <Error />

  return (
    <Box width="full" pad={responsive({ horizontal: 'medium' })}>
      <Box pad={{ bottom: 'large' }}>
        <Text serif size="xlarge">
          My Dataset
        </Text>
      </Box>
    </Box>
  )
}

export default Download
