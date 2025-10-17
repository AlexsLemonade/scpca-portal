import React from 'react'
import { Anchor, Box, Grid, Heading } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { config } from 'config'
import HappyMusic from '../images/happy-music.svg'

export const DatasetResourceLinks = () => {
  const { responsive } = useResponsive()

  return (
    <Grid
      areas={responsive([['img'], ['content']], [['img', 'content']])}
      columns={responsive(['auto'], ['1/4', '2/4'])}
      justifyContent="center"
    >
      <Box gridArea="img" align={responsive('center', 'start')}>
        <HappyMusic />
      </Box>
      <Box gridArea="content" pad={{ right: 'small' }}>
        <Heading level={1} serif size="38px" margin={{ bottom: 'medium' }}>
          Get ready to analyze your ScPCA dataset
        </Heading>
        <Box direction="column" gap="medium">
          <Anchor
            href={`${config.links.what_downloading}`}
            target="_blank"
            label="Learn more about what to expect in your download"
            size="21px"
          />
          <Anchor
            href={`${config.links.getting_started}`}
            target="_blank"
            label=" Getting started with a ScPCA dataset"
            size="21px"
          />
          <Anchor
            href={`${config.links.frequently_asked_questions}`}
            target="_blank"
            label="Frequently asked questions"
            size="21px"
          />
        </Box>
      </Box>
    </Grid>
  )
}

export default DatasetResourceLinks
