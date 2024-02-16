import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Grid, Paragraph, Text } from 'grommet'
import { CardBandLarge, HeroBandReversed } from 'components/Band'
import { DonateButton } from 'components/DonateButton'
import { Link } from 'components/Link'
import { config } from 'config'
import FigureFeaturesEnhancementsSvg from '../../images/about-page-fig-features-enchancements.svg'
import FigureFeaturesEnhancementsSvgMobile from '../../images/about-page-fig-features-enchancements-mobile.svg'
import FigureHowItWorksSvg from '../../images/about-page-fig-how-it-works.svg'
import FigureHowItWorksSvgMobile from '../../images/about-page-fig-how-it-works-mobile.svg'
import ChooseSvg from '../../images/choose.svg'
import ShowingSupportSvg from '../../images/showing-support.svg'

const Li = ({ text }) => (
  <Box as="li" style={{ display: 'list-item' }}>
    {text}
  </Box>
)

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
          <FigureHowItWorksSvgMobile
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
                href="/"
                label="View the current number of tumor types represented and samples being processed here"
                newTab
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
          <Box pad={{ horizontal: 'xlarge' }} align="end">
            {responsive(
              '',
              <FigureHowItWorksSvg
                role="img"
                aria-label="A diagram image for How it works"
              />
            )}
          </Box>
        </Box>
      </Grid>
      <Box background="dawn" width="full" align="center" pad={{ top: 'large' }}>
        <Box
          width={{ max: 'xlarge' }}
          fill
          pad={responsive({ horizontal: 'medium' })}
        >
          <Text size="xlarge">Features and Enhancements</Text>
        </Box>
        <Box align="center" width={{ width: 'full', max: 'xlarge' }}>
          <Box
            margin={{ top: 'large', bottom: 'xlarge' }}
            pad={responsive({ horizontal: 'medium' })}
          >
            {responsive(
              <FigureFeaturesEnhancementsSvgMobile
                role="img"
                aria-label="A diagram image for Features and Enhancements"
                width={{ max: '320px' }}
              />,
              <FigureFeaturesEnhancementsSvg
                role="img"
                aria-label="A diagram image for Features and Enhancements"
                width={responsive('', 'auto', '750px')}
              />
            )}
          </Box>
          <Grid
            columns={responsive('1', '1/2')}
            gap="xlarge"
            width={{ width: 'full', max: 'xlarge' }}
            margin={{ bottom: 'xlarge' }}
            pad={responsive('medium')}
          >
            <Box>
              <Text weight="bold">Open Source Pipeline</Text>
              <Text>
                The open-source{' '}
                <Link
                  href={config.links.ccdlGithub_pipeline}
                  label="pipeline"
                />{' '}
                pipeline used to process the data is fast, reusable, and
                cost-efficient. Others can utilize the pipeline for their own
                data, and the pipeline can be easily extended.
              </Text>
            </Box>
            <Box>
              <Text weight="bold">Community Contributions</Text>
              <Text>
                More researchers can share their single-cell data on the Portal!
                We now accept dataset contributions from pediatric cancer
                researchers outside of the initial ScPCA grant.{' '}
                <Link
                  href="/contribute"
                  label="Learn more about contributing data"
                  newTab
                />
              </Text>
            </Box>
          </Grid>
          <Grid
            align="center"
            gap="none"
            rows={['none ', 'none']}
            columns={['1', '1']}
            areas={responsive(
              [
                { name: 'left', start: [0, 0], end: [1, 0] },
                { name: 'right', start: [0, 1], end: [1, 1] }
              ],
              [
                { name: 'left', start: [0, 1], end: [0, 1] },
                { name: 'right', start: [1, 1], end: [1, 1] }
              ]
            )}
            margin={{
              top: responsive('', '72px'),
              bottom: responsive('xlarge', '72px'),
              horizontal: responsive('large', 'none')
            }}
          >
            <Box align={responsive('center', 'start')} gridArea="left">
              <ChooseSvg alt="" width={responsive('100px')} />
            </Box>

            <Box
              gridArea="right"
              margin={{ left: responsive('none', 'xlarge') }}
            >
              <Text weight="bold">More Choices for Users</Text>
              <Text>
                Researchers can choose which file format to receive when
                downloading data. Downloads can be immediately used with two
                major software ecosystems for working with single-cell data.
                This means more users can avoid the time-consuming process of
                converting their ScPCA data to their preferred format and start
                working with it faster.
              </Text>
            </Box>
          </Grid>
        </Box>
      </Box>
      <Box width={{ max: 'xlarge' }}>
        <Grid
          align="end"
          gap="none"
          rows={['none ', 'none']}
          columns={['1', '1']}
          areas={responsive(
            [
              { name: 'left', start: [0, 0], end: [1, 0] },
              { name: 'right', start: [0, 1], end: [1, 1] }
            ],
            [
              { name: 'left', start: [0, 1], end: [0, 1] },
              { name: 'right', start: [1, 1], end: [1, 1] }
            ]
          )}
          margin={{
            top: responsive('xlarge', 'xlarge'),
            bottom: responsive('none', 'medium'),
            horizontal: responsive('large', 'none')
          }}
        >
          <Box
            gridArea="left"
            margin={{ right: responsive('none', 'xlarge') }}
            pad={{ left: 'none' }}
          >
            <Box width={{ max: 'xlarge' }} fill margin={{ bottom: 'medium' }}>
              <Text size="xlarge">Support the Data Lab</Text>
            </Box>
            <Paragraph margin={{ bottom: 'large' }}>
              The ScPCA has the potential to serve the pediatric cancer research
              community and change the lives of children fighting cancer in even
              more ways!
            </Paragraph>
            <Paragraph margin={{ bottom: 'large' }}>
              With your support, we will:
            </Paragraph>
            <Box as="ul" pad={{ left: '26px' }} style={{ listStyle: 'disc' }}>
              <Li
                text="Continue to expand features that will help researchers get
                further with their data"
              />
              <Li
                text="Grow the Portal by making more data available through community
                contributions"
              />
              <Li
                text="Launch a global, open science initiative to improve the utility
                of the ScPCA data"
              />
            </Box>
          </Box>
          <Box align={responsive('center', 'start')} gridArea="right">
            <ShowingSupportSvg alt="" width={responsive('120px')} />
          </Box>
        </Grid>
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
