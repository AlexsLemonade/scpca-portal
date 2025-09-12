import React from 'react'
import { Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { api } from 'api'

// eslint-disable-next-line no-unused-vars
const Dataset = ({ dataset }) => {
  const { responsive } = useResponsive()

  // TODO: Remove temporary log after completing integration
  // eslint-disable-next-line no-console
  console.log({ dataset })

  return (
    <Box width="full" pad={responsive({ horizontal: 'medium' })}>
      <Box pad={{ bottom: 'large' }}>
        <Text serif size="xlarge">
          Dataset
        </Text>
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
