import React from 'react'
import { useRouter } from 'next/router'
import { Box, Text } from 'grommet'
import { api } from 'api'
import { Button } from 'components/Button'
import ErrorImage from '../images/503-illustration.svg'

// Refresh the locally stored dataset in case a stale shape caused the error
const refreshLocalDataset = async () => {
  try {
    const stored = JSON.parse(window.localStorage.getItem('dataset'))
    if (!stored?.id) return

    const datasetRequest = await api.datasets.get(stored.id)
    if (!datasetRequest.isOk) return

    window.localStorage.setItem(
      'dataset',
      JSON.stringify(datasetRequest.response)
    )
  } catch (error) {
    console.error(error)
  }
}

const ErrorPage = () => {
  const router = useRouter()

  React.useEffect(() => {
    refreshLocalDataset()
  }, [])

  React.useEffect(() => {
    const forceRefresh = (url) => {
      window.location = url
    }

    router.events.on('routeChangeStart', forceRefresh)
  })

  const goBack = () => {
    router.back()
  }

  return (
    <Box direction="row" gap="xxlarge">
      <Box justify="center" align="start">
        <Box margin={{ bottom: 'medium' }}>
          <Text size="xxlarge">We encountered an unexpected error.</Text>
          <Text size="xxlarge">Please try again later..</Text>
        </Box>
        <Button primary onClick={goBack} label="Go Back" />
      </Box>
      <ErrorImage />
    </Box>
  )
}

export default ErrorPage
