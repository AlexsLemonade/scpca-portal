import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { CopyLinkButton } from 'components/CopyLinkButton'
import { DatasetDownloadToken } from 'components/DatasetDownloadToken'
import { Link } from 'components/Link'
import DownloadReady from '../images/download-folder.svg'

export const DatasetHeroReady = ({
  isToken = false // temporary for Storybook
}) => {
  const { responsive } = useResponsive()
  const [token, setToken] = useState(isToken)

  // temporary
  // NOTE: We handle the token generation in
  useEffect(() => {
    setToken(isToken)
  }, [isToken])

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
              Uncompressed size: 80GB
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
          <>
            <DatasetDownloadToken
              text={
                <>
                  Please read and accept our{' '}
                  <Link label="Terms of Service" href="/terms-of-use" /> and{' '}
                  <Link label="Privacy Policy" href="/privacy-policy" /> before
                  you download data.
                </>
              }
            />
            <Box
              direction={responsive('column', 'row')}
              gap="24px"
              margin={{ top: 'medium' }}
            >
              <Button primary aria-label="Submit" label="Submit" />
            </Box>
          </>
        )}
      </Box>
      <Box gridArea="img" align={responsive('center', 'start')}>
        <DownloadReady />
      </Box>
    </Grid>
  )
}

export default DatasetHeroReady
