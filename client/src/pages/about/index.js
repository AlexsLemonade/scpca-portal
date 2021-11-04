import React from 'react'
import { Box, Grid, Paragraph, Text } from 'grommet'
import { HeroBandReversed, CardBandLarge } from 'components/Band'
import { DonateButton } from 'components/DonateButton'
import AboutPageFigure from '../../images/about-page-figure.svg'
import SaveTime from '../../images/save-time.svg'
import WidelyAvailable from '../../images/widely-available.svg'
import OpenSource from '../../images/open-source.svg'
import Access from '../../images/access.svg'

export const About = () => {
  return (
    <>
      <HeroBandReversed
        background="dawn"
        width="full"
        align="center"
        pad={{ top: 'xxlarge' }}
      >
        <Box width={{ max: 'xlarge' }} fill pad={{ top: 'medium' }}>
          <Text size="xxlarge">About</Text>
        </Box>
        <Box width={{ max: 'large' }} pad={{ top: 'large', bottom: 'large' }}>
          <Paragraph size="large" textAlign="center">
            The Single-cell Pediatric Cancer Atlas (ScPCA) is accelerating the
            discovery of better treatments for pediatric solid tumors and
            leukemias. Single-cell profiling can provide insight into how
            certain cells influence cancer progression and treatment response.
          </Paragraph>
        </Box>
      </HeroBandReversed>
      <Box width="full" align="center" pad={{ vertical: 'large' }}>
        <Box width={{ max: 'xlarge' }} fill>
          <Text size="xlarge">How it works</Text>
        </Box>
      </Box>
      <Box>
        <AboutPageFigure />
      </Box>
      <Grid
        columns="1/2"
        gap="xxlarge"
        pad={{ top: 'large', bottom: 'xlarge' }}
        width={{ max: 'xlarge' }}
      >
        <Box pad={{ right: 'xxlarge' }}>
          <Text weight="bold">
            ALSF funds cutting-edge pediatric cancer research
          </Text>
          <Text>
            Alex’s Lemonade Stand Foundation (ALSF) funded 10 childhood cancer
            investigators from eight different institutions working on
            single-cell profiling to create a publicly available atlas of
            single-cell pediatric cancer data. Learn more about the grants
            program.
          </Text>
        </Box>
        <Box pad={{ right: 'xxlarge' }}>
          <Text weight="bold">The Data Lab processes the generated data</Text>
          <Text>
            ALSF’s Childhood Cancer Data Lab is trusted to process the
            single-cell, single-nuclei, and bulk RNA sequencing data submitted
            by the ALSF-funded investigators. You can view the current number of
            tumor types represented and samples being processed here.
          </Text>
        </Box>
      </Grid>
      <Box background="dawn" width="full" align="center" pad={{ top: 'large' }}>
        <Box align="start" width={{ max: 'xlarge' }} fill>
          <Text size="xlarge">Impact</Text>
        </Box>
        <Box align="center" width={{ max: 'xlarge' }}>
          <Box margin={{ vertical: 'large' }}>
            <Text>
              ALSF’s funding and the Data Lab’s expertise maximize the reach of
              this open resource to accelerate the rate of new discoveries.
            </Text>
          </Box>
          <Grid columns="1/2" gap="xlarge" margin={{ bottom: 'xlarge' }}>
            <Box direction="row" justify="between" gap="medium">
              <Box width="24px">
                <Access />
              </Box>
              <Box>
                <Text weight="bold">Accessible Cutting-edge Technology</Text>
                <Text>
                  Single-cell RNA sequencing is a cutting-edge technology and
                  may not be accessible to all childhood cancer experts. Making
                  the outputs of this project readily and openly available puts
                  data in the hands of more researchers.
                </Text>
              </Box>
            </Box>
            <Box direction="row" justify="between" gap="medium">
              <Box width="24px">
                <WidelyAvailable />
              </Box>
              <Box>
                <Text weight="bold">Widely Available</Text>
                <Text>
                  The Data Lab developed the ScPCA Portal to make the data from
                  these patient samples widely and easily available in one
                  location.
                </Text>
              </Box>
            </Box>
            <Box direction="row" justify="between" gap="medium">
              <Box width="24px">
                <OpenSource />
              </Box>
              <Box>
                <Text weight="bold">Open Source</Text>
                <Text>
                  The pipeline used to process the data is open source and well
                  documented. This not only cultivates trust in the data, but
                  also enables researchers to utilize the pipeline for their own
                  analyses and ensure reproducible results.
                </Text>
              </Box>
            </Box>
            <Box direction="row" justify="between" gap="medium">
              <Box width="24px">
                <SaveTime />
              </Box>
              <Box>
                <Text weight="bold">Frees up Researcher Time</Text>
                <Text>
                  This saves precious time for researchers who would have
                  otherwise had to process the data themselves and enables them
                  to begin using it immediately.
                </Text>
              </Box>
            </Box>
          </Grid>
        </Box>
      </Box>
      <Box width={{ max: 'xlarge' }}>
        <Box pad={{ vertical: 'xlarge' }}>
          <CardBandLarge
            pad={{
              top: 'xlarge',
              right: 'xxlarge',
              bottom: 'large',
              left: 'xxlarge'
            }}
            elevation="medium"
          >
            <Text size="large" weight="bold">
              Donate
            </Text>
            <Box direction="row" align="center" gap="xxlarge">
              <Text>
                Innovative projects like the Single-cell Pediatric Cancer Atlas
                are made possible by generous donors. Support impactful research
                by donating to ALSF’s Childhood Cancer Data Lab today!
              </Text>
              <Box flex="grow">
                <DonateButton label="Donate Now" />
              </Box>
            </Box>
          </CardBandLarge>
        </Box>
      </Box>
    </>
  )
}

export default About
