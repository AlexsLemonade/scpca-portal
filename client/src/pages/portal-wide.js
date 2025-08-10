import React from 'react'
import { Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { api } from 'api'
import Error from 'pages/_error'

// NOTE: This page is used to display CCDL datasets
const Datasets = ({ datasets }) => {
  const { responsive } = useResponsive()

  // we don't want to 404 here we want to show that the api is down
  if (!datasets) return <Error />

  return (
    <Box width="full" pad={responsive({ horizontal: 'medium' })}>
      <Box pad={{ bottom: 'large' }}>
        <Text serif size="xlarge">
          CCDL Datasets
        </Text>
      </Box>
    </Box>
  )
}

export const getServerSideProps = async ({ query }) => {
  // default limit is 10, so here we will set it to 100 unless specified
  const queryWithDefaultLimit = { ...query, limit: query.limit || 100 }

  const datasetRequest = await api.datasets.list(queryWithDefaultLimit)

  if (datasetRequest.isOk) {
    // TODO: Replace with response.results if required (currently returns an array of CCDL datasets)
    const datasets = datasetRequest.response || []
    return {
      props: { datasets }
    }
  }

  return { props: { datasets: null } }
}

export default Datasets
