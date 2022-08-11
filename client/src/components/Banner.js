import React, { useEffect } from 'react'
import { useBanner } from 'hooks/useBanner'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Paragraph } from 'grommet'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'

export const Banner = ({
  background = 'brand',
  color = 'white',
  ctaLabel,
  ctaLink,
  label,
  iconColor = 'brand',
  iconName = null,
  iconSize = '24px',
  children
}) => {
  const { showing, hideBanner, showBanner } = useBanner()
  const { responsive } = useResponsive()

  useEffect(() => {
    showBanner()
  }, [])

  return (
    <>
      {showing && (
        <Box
          background={background}
          direction="row"
          justify="between"
          width="100%"
          height="56px"
        >
          <Box direction="row" align="center" justify="center" flex="grow">
            {children || (
              <>
                {iconName && (
                  <Icon
                    color={iconColor}
                    name={iconName}
                    size={iconSize}
                    aria-hidden="true"
                  />
                )}
                <Paragraph
                  color={color}
                  margin={{ left: '4px' }}
                  size={responsive('medium', 'large')}
                >
                  {label}{' '}
                  <Link
                    color={color}
                    href={ctaLink}
                    label={ctaLabel}
                    underline
                  />
                </Paragraph>
              </>
            )}
          </Box>
          <Box pad="20px" onClick={() => hideBanner()}>
            <Icon name="Cross" size="16px" color={color} />
          </Box>
        </Box>
      )}
    </>
  )
}
export default Banner
