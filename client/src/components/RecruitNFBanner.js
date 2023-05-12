import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Paragraph } from 'grommet'
import { Banner } from 'components/Banner'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'
import { config } from 'config'

export const RecruitNFContentBlock = () => {
  const { responsive } = useResponsive()

  return (
    <Box direction="row" align="center" justify="center" flex="grow">
      <Icon color="brand" name="htmlGear" size="24px" aria-hidden="true" />
      <Paragraph
        color="black"
        margin={{ left: 'xsmall' }}
        size={responsive('medium', 'large')}
      >
        Processing your own single-cell data?{' '}
        <Link
          color="black"
          href={config.links.recruitment_hsform}
          label="Sign up to test our pipeline"
          underline
        />
      </Paragraph>
    </Box>
  )
}

export const RecruitNFBanner = ({ id = 'recruit-nf', ...props }) => {
  return (
    // eslint-disable-next-line react/jsx-props-no-spreading
    <Banner id={id} background="alexs-lemonade-tint-40" {...props}>
      <RecruitNFContentBlock />
    </Banner>
  )
}

export default RecruitNFBanner
