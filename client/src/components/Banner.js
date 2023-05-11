import React, { useEffect, useRef } from 'react'
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
  showByDefault = true,
  children
}) => {
  const { show, hideBanner, showBanner, setBannerHeight } = useBanner()
  const { responsive } = useResponsive()
  const bannerRef = useRef(null)

  useEffect(() => {
    if (showByDefault) showBanner()

    setBannerHeight(bannerRef.current?.clientHeight)
  }, [])

  if (!show) return null

  return (
    <Box background={background} direction="row" justify="between" width="100%">
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
              margin={{ left: 'xsmall' }}
              size={responsive('medium', 'large')}
            >
              {label}{' '}
              <Link color={color} href={ctaLink} label={ctaLabel} underline />
            </Paragraph>
          </>
        )}
      </Box>
      <Box pad="20px" onClick={() => hideBanner()}>
        <Icon name="Cross" size="16px" color={color} />
      </Box>
    </Box>
  )
}
export default Banner
