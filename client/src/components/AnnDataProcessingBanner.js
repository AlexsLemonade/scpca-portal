import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Paragraph } from 'grommet'
import { Banner } from 'components/Banner'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'
import { config } from 'config'

export const AnnDataProcessingBanner = ({
  id = 'ann-data-processing',
  ...props
}) => {
  const { responsive } = useResponsive()
  return (
    // eslint-disable-next-line react/jsx-props-no-spreading
    <Banner id={id} background="alexs-lemonade-tint-75" {...props}>
      <Box pad={{ vertical: 'large' }}>
        <Box
          direction={responsive('column', 'row')}
          align="center"
          justify="center"
          flex="grow"
        >
          <Icon
            color="error"
            name="WarningNoFill"
            size="24px"
            aria-hidden="true"
          />
          <Paragraph
            color="black"
            margin={{ left: 'xsmall' }}
            size={responsive('medium', 'large')}
            textAlign="center"
          >
            We are making{' '}
            <Link
              color="black"
              href={config.links.recruitment_hsform}
              label="AnnData"
            />{' '}
            available on the portal and it will take several hours to complete.
          </Paragraph>
        </Box>
        <Box pad={{ horizontal: 'medium' }}>
          <Paragraph
            color="black"
            size={responsive('medium', 'large')}
            textAlign="center"
          >
            During this time, AnnData might not be available for all projects
            and you might experience some disruptions to normal service.
          </Paragraph>
        </Box>
      </Box>
    </Banner>
  )
}

export default AnnDataProcessingBanner
