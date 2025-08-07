import React from 'react'
import { Anchor, Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { api } from 'api'

const PortalWideDownloads = () => {
  const { responsive } = useResponsive()

  return (
    <Box alignSelf="start" pad={{ left: 'medium' }} margin={{ top: 'none' }}>
      <Box pad={{ bottom: 'medium' }}>
        <Text serif size="xlarge" weight="bold">
          Portal-wide Downloads
        </Text>
      </Box>
      <Box pad={{ top: 'large' }}>
        <Text serif size="medium" margin={{ top: 'small' }}>
          Data from the projects in the ScPCA portal is packaged together for
          your convenience.
          <Anchor
            label=" Please learn more about the portal-wide downloads here."
            href="#"
          />
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

export default PortalWideDownloads
