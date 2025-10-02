import React from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useResponsive } from 'hooks/useResponsive'
import { formatBytes } from 'helpers/formatBytes'
import { Button } from 'components/Button'
import { CopyLinkButton } from 'components/CopyLinkButton'
import { DatasetDownloadForm } from 'components/DatasetDownloadForm'
import DownloadReady from '../images/download-folder.svg'

export const DatasetHeroReady = ({ dataset }) => {
  const { responsive } = useResponsive()
  const { token } = useScPCAPortal()

  return (
    <Grid
      areas={responsive(
        [['header'], ['img'], ['content']],
        [
          ['header', 'header'],
          ['content', 'img']
        ]
      )}
      columns={responsive(['auto'], ['3/5', '2/5'])}
      justifyContent="center"
    >
      <Box gridArea="header" margin={{ bottom: 'medium' }}>
        <Heading level={1} serif size="38px">
          Your dataset is ready!
        </Heading>
      </Box>

      <Box gridArea="content" pad={{ right: 'small' }}>
        {token ? (
          <Box direction="column">
            <Paragraph size="21px">
              Your dataset will be available for immediate download for 7 days.
            </Paragraph>
            <Paragraph size="21px" margin={{ bottom: 'medium' }}>
              After it expires, you can come back to this page to regenerate and
              download the dataset.
            </Paragraph>
            <Text margin={{ bottom: 'small' }} weight="bold">
              Uncompressed size: {formatBytes(dataset.estimated_size_in_bytes)}
            </Text>
            <Box
              direction={responsive('column', 'row')}
              gap="24px"
              margin={{ bottom: 'small' }}
            >
              <Button primary aria-label="Download" label="Download" />
              <CopyLinkButton computedFile={{}} />
            </Box>
          </Box>
        ) : (
          <DatasetDownloadForm />
        )}
      </Box>
      <Box gridArea="img" align={responsive('center', 'start')}>
        <DownloadReady />
      </Box>
    </Grid>
  )
}

export default DatasetHeroReady
