import React from 'react'
import { useRouter } from 'next/router'
import { Box, Text } from 'grommet'
import { Button } from 'components/Button'
import ErrorImage from '../images/503-illustration.svg'

const ErrorPage = () => {
  const router = useRouter()

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
    <Box direction="row" align="center" gap="xxlarge">
      <Box align="start">
        <Box margin={{ bottom: 'medium' }}>
          <Text size="xxlarge">This page does not exist.</Text>
        </Box>
        <Button primary onClick={goBack} label="Go Back" />
      </Box>
      <ErrorImage />
    </Box>
  )
}

export default ErrorPage
