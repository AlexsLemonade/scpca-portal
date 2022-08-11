import React, { useEffect } from 'react'
import { useBanner } from 'hooks/useBanner'
import { Box, Paragraph } from 'grommet'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'

export const Banner = ({
  label,
  bgColor = 'brand',
  ctaLabel,
  ctaLink,
  fontColor = 'white',
  iconColor = 'brand',
  iconName = null,
  iconSize = '24px',
  children
}) => {
  const { showing, handleHideBanner, handleShowBanner } = useBanner()

  useEffect(() => {
    handleShowBanner()
  }, [])

  return (
    <>
      {showing && (
        <Box
          background={bgColor}
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
                  color={fontColor}
                  margin={{ left: '4px' }}
                  size="21px"
                >
                  {label}{' '}
                  <Link
                    color={fontColor}
                    href={ctaLink}
                    label={ctaLabel}
                    underline
                  />
                </Paragraph>
              </>
            )}
          </Box>
          <Box pad="20px" onClick={() => handleHideBanner()}>
            <Icon name="Cross" size="16px" color={fontColor} />
          </Box>
        </Box>
      )}
    </>
  )
}
export default Banner
