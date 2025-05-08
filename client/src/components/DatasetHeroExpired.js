import React from 'react'
import { Box, Grid, Heading, Paragraph } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { InfoText } from 'components/InfoText'
import DownloadExpired from '../images/download-expired.svg'

export const DatasetHeroExpired = () => {
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
          Your dataset has expired
        </Heading>
      </Box>

      <Box gridArea="content" direction="column" pad={{ right: 'small' }}>
        <Paragraph margin={{ bottom: '44px' }} size="21px">
          The dataset isn’t available for download anymore. Please regenerate
          the files to download them again.
        </Paragraph>
        <Box
          direction={responsive('column', 'row')}
          margin={{ bottom: 'small' }}
        >
          <Button
            primary
            aria-label="Regenerate Dataset"
            label="Regenerate Dataset"
          />
        </Box>
        <InfoText
          label={
            <>
              Some values may have changed.{' '}
              <Link href="#demo" label="Learn more" />
            </>
          }
        />
      </Box>
      <Box gridArea="img" align={responsive('center', 'start')}>
        <DownloadExpired />
      </Box>
    </Grid>
  )
}

export default DatasetHeroExpired
