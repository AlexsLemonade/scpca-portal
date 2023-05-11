import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Paragraph } from 'grommet'
import { Banner } from 'components/Banner'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'
import { config } from 'config'

export const RecruitNFBanner = () => {
  const { responsive } = useResponsive()

  return (
    <Banner id="recruit-nf" background="alexs-lemonade-tint-40">
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
    </Banner>
  )
}

export default RecruitNFBanner
