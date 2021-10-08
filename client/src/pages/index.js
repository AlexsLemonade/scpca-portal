import React from 'react'
import {
  Box,
  FormField,
  Image,
  Paragraph,
  Stack,
  TextInput,
  Text
} from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { api } from 'api'
import { HeroBand, CardBand } from 'components/Band'
import { ErrorLabel } from 'components/ErrorLabel'
import styled, { css } from 'styled-components'
import { getStatsBlocks } from 'helpers/getStatsBlocks'
import { fillArrayRandom } from 'helpers/fillArrayRandom'
import { ScPCAPortalContext } from 'contexts/ScPCAPortalContext'
import { config } from 'config'
import PipelineSvg from '../images/pipeline.svg'
import FilesSvg from '../images/files.svg'

const ExposeBox = styled(Box)`
  > div {
    transition: height 0.1s ease-in;
  }

  ${({ exposed }) => {
    if (['none', 'some'].includes(exposed)) {
      return css`
        position: relative;

        > div {
          height: ${exposed === 'none' ? '180px' : '320px'};
          overflow-y: hidden;
          &:after {
            content: '';
            display: block;
            position: absolute;
            background-repeat: no-repeat;
            background-image: radial-gradient(
              rgba(255, 255, 255, 1),
              transparent
            );
            height: 156px;
            bottom: 0;
            left: 0;
            right: 0;
          }
        }
        > button {
          z-index: 1;
        }
      `
    }
    return ''
  }}
`

const Home = ({ stats }) => {
  const { emailListForm } = React.useContext(ScPCAPortalContext)

  const statBlocks = getStatsBlocks(stats)
  const cancerColors = React.useMemo(
    () =>
      fillArrayRandom(
        stats.cancer_types.length,
        'alexs-deep-blue-tint-70',
        'alexs-lemonade-tint-75',
        'alexs-light-blue-tint-60'
      ),
    []
  )

  const [exposed, setExposed] = React.useState(
    stats.cancer_types.length > 10 ? 'none' : 'all'
  )

  const exposeMore = () => {
    if (exposed === 'none') return setExposed('some')
    return setExposed('all')
  }

  return (
    <>
      <HeroBand
        background="dawn"
        width="full"
        align="center"
        pad={{ top: 'xxlarge' }}
      >
        <Box
          width="full"
          background="alexs-light-blue"
          align="center"
          pad={{ bottom: 'small' }}
        >
          <Text size="xxlarge">Single-cell Pediatric Cancer Atlas Portal</Text>
        </Box>
        <Box width="medium" pad={{ top: 'large', bottom: 'large' }}>
          <Paragraph size="large" textAlign="center">
            Database of single-cell data from pediatric cancer clinical samples
            and xenografts
          </Paragraph>
        </Box>
        <Box pad={{ bottom: 'large' }}>
          <Button primary label="Browse Portal" href="/projects" />
        </Box>
      </HeroBand>
      <Box width="full" align="center" pad={{ vertical: 'large' }}>
        <Text size="xlarge">ScPCA Portal currently has</Text>
        <Box
          width="full"
          pad={{ vertical: 'large' }}
          background="linear-gradient(0deg, rgba(237,247,253,1) 50%, transparent 50%)"
          align="center"
        >
          <Box direction="row" gap="xxlarge" width="xlarge">
            {statBlocks.map((sb) => (
              <CardBand
                key={sb.name}
                elevation="medium"
                basis="1/4"
                align="center"
                pad={{ vertical: 'xlarge' }}
                background="white"
              >
                <Text size="large">{sb.value}</Text>
                <Text size="large">{sb.name}</Text>
              </CardBand>
            ))}
          </Box>
        </Box>
        <Box
          align="center"
          width="full"
          background="dawn"
          pad={{ top: 'large' }}
        >
          <Text size="xlarge">Explore the available cancer types.</Text>
          <ExposeBox
            width="xlarge"
            pad={{ vertical: 'medium' }}
            align="center"
            exposed={exposed}
          >
            <Box
              direction="row"
              wrap
              align="center"
              pad={{ vertical: 'large' }}
            >
              {stats.cancer_types.map((ct, i) => (
                <Link key={ct} href={`/projects?diagnoses=${ct}`}>
                  <Box
                    round
                    background={cancerColors[i]}
                    pad={{ vertical: 'xsmall', horizontal: 'small' }}
                    margin="small"
                  >
                    <Text wordBreak="keep-all">{ct}</Text>
                  </Box>
                </Link>
              ))}
            </Box>
            {exposed !== 'all' && (
              <Button primary onClick={exposeMore} label="Show More..." />
            )}
          </ExposeBox>
        </Box>
      </Box>
      <Box align="center" pad={{ vertical: 'large' }}>
        <Box
          direction="row"
          gap="large"
          width={{ max: '250px' }}
          align="center"
          pad={{ bottom: 'large' }}
        >
          <Box>
            <Image src="/alsf-logo.png" />
          </Box>
          <Text size="xlarge" weight="bold">
            X
          </Text>
          <Box>
            <Image src="/ccdl-logo.png" />
          </Box>
        </Box>
        <Box width="medium" pad={{ vertical: 'medium' }}>
          <Paragraph textAlign="center">
            Alex’s Lemonade Stand Foundation (ALSF) funded 10 childhood cancer
            investigators from 8 different institutions working on single-cell
            profiling to create a publicly available atlas of single-cell
            pediatric cancer data.
          </Paragraph>
        </Box>
        <Button primary label="Learn More" href="/about" />
      </Box>
      <Box
        width="full"
        align="center"
        background="dawn"
        pad={{ vertical: 'xlarge' }}
      >
        <Box width="xlarge" align="center" direction="row" gap="xlarge">
          <Stack anchor="bottom-right">
            <Box
              background="white"
              elevation="medium"
              pad={{ top: 'large', bottom: 'medium', horizontal: 'large' }}
              basis="1/2"
            >
              <Text weight="bold">How is the data processed?</Text>
              <Box pad={{ vertical: 'medium', right: 'xxlarge' }}>
                <Paragraph>
                  All of the data is uniformly processed with an open source and
                  freely available pipeline which uses alevin-fry, and
                  Bioconductor packages.
                </Paragraph>
              </Box>
              <Button
                alignSelf="start"
                label="Learn More"
                href={config.links.how_processed}
              />
            </Box>
            <Box margin={{ top: '6px' }}>
              <FilesSvg />
            </Box>
          </Stack>
          <Stack anchor="bottom-right">
            <Box
              background="white"
              elevation="medium"
              pad={{ top: 'large', bottom: 'medium', horizontal: 'large' }}
              basis="1/2"
            >
              <Text weight="bold">What am I downloading?</Text>
              <Box pad={{ vertical: 'medium', right: 'xxlarge' }}>
                <Paragraph>
                  When you download from the ScPCA Portal, you will receive both
                  filtered and unfiltered count matrices for each sample along
                  with sample and project metadata.
                </Paragraph>
              </Box>
              <Button
                alignSelf="start"
                label="Learn More"
                href={config.links.what_downloading}
              />
            </Box>
            <Box margin={{ top: '6px' }}>
              <PipelineSvg />
            </Box>
          </Stack>
        </Box>
      </Box>
      <Box align="center" pad={{ vertical: 'large' }}>
        <Text size="xlarge">Sign up for updates</Text>
        <Text size="large">
          Receive updates about new datasets and updates to the portal.
        </Text>
        <Box direction="row" gap="medium" pad={{ vertical: 'medium' }}>
          <FormField
            width="280px"
            error={
              emailListForm.hasError && (
                <ErrorLabel error={emailListForm.errors.email} />
              )
            }
          >
            <TextInput
              value={emailListForm.getAttribute('email') || ''}
              onChange={({ target: { value } }) => {
                emailListForm.setAttribute('email', value)
              }}
            />
          </FormField>
          <Box margin={{ top: 'medium', bottom: 'small' }}>
            <Button
              primary
              disabled={emailListForm.hasError}
              label="Subscribe"
              onClick={async () => {
                if (await emailListForm.validate().isValid)
                  emailListForm.submit()
              }}
            />
          </Box>
        </Box>
        {emailListForm.success && (
          <Box>
            <Text color="success">Thank you for signing up!</Text>
          </Box>
        )}
      </Box>
    </>
  )
}

export const getStaticProps = async () => {
  const statsRequest = await api.stats.get()

  if (statsRequest.isOk) {
    const stats = statsRequest.response
    return {
      props: { stats },
      revalidate: 60 * 60 * 24 * 7 // one week in seconds
    }
  }

  return { props: { stats: {} }, revalidate: 60 }
}

export default Home
