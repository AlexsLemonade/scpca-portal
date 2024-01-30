import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Grid, Paragraph, Text } from 'grommet'
import { CardBandLarge, HeroBandReversed } from 'components/Band'
import { DonateButton } from 'components/DonateButton'
import { Link } from 'components/Link'
import { config } from 'config'
import AboutPageFigure from '../../images/about-page-figure.svg'
import AboutPageFigureMobile from '../../images/about-page-fig-mobile.svg'
import SaveTime from '../../images/save-time.svg'
import WidelyAvailable from '../../images/widely-available.svg'
import OpenSource from '../../images/open-source.svg'
import Access from '../../images/access.svg'

export const About = () => {
  const { responsive } = useResponsive()

  return (
    <>
      <HeroBandReversed
        background="dawn"
        width="full"
        align="center"
        pad={{ top: '92px' }}
      >
        <Box
          width={{ max: 'xlarge' }}
          fill
          pad={responsive({ horizontal: 'medium' }, { top: 'large' })}
        >
          <Text size="xxlarge">About</Text>
        </Box>
        <Box
          width={{ max: 'large' }}
          pad={responsive(
            { top: 'xlarge', bottom: 'large' },
            { top: 'large', bottom: 'large' }
          )}
        >
          <Paragraph size="large" textAlign="center">
            The Single-cell Pediatric Cancer Atlas (ScPCA) is enabling broad
            access to single-cell data from pediatric cancer tumors and model
            systems will increase its impact on the lives of children with
            cancer. The Single-cell Pediatric Cancer Atlas (ScPCA) was created
            to generate an unprecedented resource for the pediatric cancer
            research community
          </Paragraph>
        </Box>
      </HeroBandReversed>
      <Box width="full" align="center" pad={{ vertical: 'large' }}>
        <Box
          width={{ max: 'xlarge' }}
          fill
          pad={responsive({ horizontal: 'medium' })}
        >
          <Text size="xlarge">Building the ScPCA Portal</Text>
        </Box>
      </Box>
      <Box pad={{ horizontal: 'medium' }}>
        {responsive(
          <AboutPageFigureMobile
            style={{ maxWidth: '100%' }}
            role="img"
            title="A diagram image for How it works"
          />
        )}
      </Box>
      <Grid
        columns={responsive('1', '1/2')}
        gap="xxlarge"
        pad={{ top: 'large', bottom: 'xlarge' }}
        width={{ width: 'full', max: 'xlarge' }}
      >
        <Box pad={responsive({ horizontal: 'medium' })}>
          <Box margin={{ bottom: responsive('xlarge', '76px') }}>
            <Text weight="bold">
              ALSF funds cutting-edge pediatric cancer research
            </Text>
            <Text>
              In 2019, Alex’s Lemonade Stand Foundation (ALSF) funded 10 grants
              for investigators working on single-cell profiling of patient
              samples to create a publicly available atlas of single-cell
              pediatric cancer data. .
            </Text>
            <Text margin={{ top: 'medium' }}>
              <Link
                href={config.links.grants_program}
                label="Learn more about the grants
            program"
              />
            </Text>
          </Box>
          <Box margin={{ bottom: responsive('xlarge', '76px') }}>
            <Text weight="bold">The Data Lab processes the generated data</Text>
            <Text>
              In 2019, Alex’s Lemonade Stand Foundation (ALSF) funded 10 grants
              for investigators working on single-cell profiling of patient
              samples to create a publicly available atlas of single-cell
              pediatric cancer data.
            </Text>
            <Text margin={{ top: 'medium' }}>
              <Link
                href={config.links.scpca}
                label="View the current number of tumor types represented and samples being processed here."
              />
            </Text>
          </Box>
          <Box margin={{ bottom: responsive('xlarge', '76px') }}>
            <Text weight="bold">The data was made widely available</Text>
            <Text>
              The ScPCA Portal launched in 2022. It was built by the Data Lab to
              make all uniformly processed data widely and readily available in
              one location.
            </Text>
          </Box>
          <Box margin={{ bottom: responsive('xlarge', '76px') }}>
            <Text weight="bold">Researchers save precious time</Text>
            <Text>
              Researchers anywhere have access to a growing database of
              single-cell data, which they can immediately begin using for their
              own research.
            </Text>
          </Box>
        </Box>

        <Box pad={responsive({ horizontal: 'medium' })}>
          <Box pad={{ horizontal: 'medium' }}>
            {responsive(
              '',
              <AboutPageFigure
                role="img"
                aria-label="A diagram image for How it works"
              />
            )}
          </Box>
        </Box>
      </Grid>
      <Box background="dawn" width="full" align="center" pad={{ top: 'large' }}>
        <Box
          align="start"
          width={{ width: 'full', max: 'xlarge' }}
          fill
          pad={responsive({ horizontal: 'medium' })}
        >
          <Text size="xlarge">Impact</Text>
        </Box>
        <Box align="center" width={{ width: 'full', max: 'xlarge' }}>
          <Box
            margin={{ vertical: 'large' }}
            pad={responsive({ horizontal: 'medium' })}
          >
            <Text>
              ALSF’s funding and the Data Lab’s expertise maximize the reach of
              this open resource to accelerate the rate of new discoveries.
            </Text>
          </Box>
          <Grid
            columns={responsive('1', '1/2')}
            gap="xlarge"
            width={{ width: 'full', max: 'xlarge' }}
            margin={{ bottom: 'xlarge' }}
            pad={responsive('medium')}
          >
            <Box
              direction="row"
              justify="between"
              gap={responsive('large', 'medium')}
            >
              <Box width="24px">
                <Access
                  role="presentation"
                  aria-hidden="true"
                  focusable="false"
                />
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
            <Box
              direction="row"
              justify="between"
              gap={responsive('large', 'medium')}
            >
              <Box width="24px">
                <WidelyAvailable
                  role="presentation"
                  aria-hidden="true"
                  focusable="false"
                />
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
            <Box
              direction="row"
              justify="between"
              gap={responsive('large', 'medium')}
            >
              <Box width="24px">
                <OpenSource
                  role="presentation"
                  aria-hidden="true"
                  focusable="false"
                />
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
            <Box
              direction="row"
              justify="between"
              gap={responsive('large', 'medium')}
            >
              <Box width="24px">
                <SaveTime
                  role="presentation"
                  aria-hidden="true"
                  focusable="false"
                />
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
            pad={responsive(
              {
                horizontal: 'large',
                vertical: 'xlarge'
              },
              {
                top: 'xlarge',
                right: 'xxlarge',
                bottom: 'large',
                left: 'xxlarge'
              }
            )}
            elevation="medium"
            background={responsive('none')}
          >
            <Text size="large" weight="bold">
              Donate
            </Text>
            <Box
              direction={responsive('column', 'row')}
              align="center"
              gap={responsive('medium', 'xxlarge')}
            >
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
