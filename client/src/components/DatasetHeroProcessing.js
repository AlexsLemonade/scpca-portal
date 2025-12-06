import React from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useResponsive } from 'hooks/useResponsive'
import DownloadProcessing from '../images/download-processing.svg'

export const DatasetHeroProcessing = () => {
  const { email } = useScPCAPortal()
  const { responsive } = useResponsive()

  return (
    <Grid
      areas={responsive(
        [['header'], ['img'], ['content']],
        [
          ['header', 'header'],
          ['content', 'img']
        ]
      )}
      columns={responsive(['auto'], ['2/4', '1/4'])}
      justifyContent="center"
    >
      <Box gridArea="header" margin={{ bottom: 'medium' }}>
        <Heading level={1} serif size="38px">
          Your dataset is being processed...
        </Heading>
      </Box>

      <Box gridArea="content" direction="column" pad={{ right: 'large' }}>
        <Paragraph margin={{ bottom: '44px' }} size="21px">
          We’re putting your files together. It should take between a few hours
          to a day.
        </Paragraph>
        <Paragraph size="21px">
          We’ll email you at{' '}
          <Text weight="bold" size="inherit">
            {email || 'john.doe@example.com'}
          </Text>{' '}
          when it’s ready for download.
        </Paragraph>
      </Box>
      <Box gridArea="img" align={responsive('center', 'start')}>
        <DownloadProcessing />
      </Box>
    </Grid>
  )
}

export default DatasetHeroProcessing
