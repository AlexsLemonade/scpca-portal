import React, { useEffect } from 'react'
import { useBanner } from 'hooks/useBanner'
import { Box, Paragraph } from 'grommet'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'
import styled, { css } from 'styled-components'

export const Banner = ({
  bannerLabel,
  bgColor = 'brand',
  ctaLabel,
  ctaLink,
  fontColor = 'white',
  htmlIcon,
  iconName,
  iconSize,
  children
}) => {
  const { showing, setShowing, onBannerClose } = useBanner()
  const BannerBox = styled(Box)`
    ${({ theme }) => css`
      background-color: ${theme.global.colors[bgColor] ||
      theme.global.colors.gradient[bgColor]};
      > div {
        > p {
          > a {
            text-decoration: underline;
          }
        }
      }
    `}
  `
  useEffect(() => {
    setShowing(true)
  }, [])

  return (
    <>
      {showing && (
        <BannerBox direction="row" justify="between" width="100%" height="56px">
          <Box direction="row" align="center" justify="center" flex="grow">
            {children || (
              <>
                {iconName && (
                  <Icon name={iconName} size={iconSize} aria-hidden="true" />
                )}
                {htmlIcon && (
                  <Box aria-hidden="true" style={{ fontSize: '24px' }}>
                    {htmlIcon}
                  </Box>
                )}
                <Paragraph
                  color={fontColor}
                  margin={{ left: '4px' }}
                  size="21px"
                >
                  {bannerLabel}{' '}
                  <Link color={fontColor} href={ctaLink}>
                    {ctaLabel}
                  </Link>
                </Paragraph>
              </>
            )}
          </Box>
          <Box pad="20px" onClick={() => onBannerClose()}>
            <Icon name="Cross" size="16px" color={fontColor} />
          </Box>
        </BannerBox>
      )}
    </>
  )
}
export default Banner
