import React, { useEffect } from 'react'
import { useBanner } from 'hooks/useBanner'
import { Box } from 'grommet'
import { Icon } from 'components/Icon'

// id is required and must be unique
export const Banner = ({
  id,
  background = 'brand',
  closeIconColor = 'black',
  elevation = '',
  width = '100%',
  hidden = false,
  zIndex = 5,
  children
}) => {
  const { banner, hideBanner, openBanner } = useBanner()

  useEffect(() => {
    if (!hidden) openBanner(id)
  }, [])

  if (!banner[id]) return null

  return (
    <Box
      background={background}
      direction="row"
      justify="center"
      width="100%"
      elevation={elevation}
      style={{ zIndex }}
    >
      <Box direction="row" justify="center" width={width}>
        {children}
      </Box>
      <Box
        pad={{ vertical: 'medium', right: '24px' }}
        onClick={() => hideBanner(id)}
        align="end"
      >
        <Icon name="Cross" color={closeIconColor} size="16px" />
      </Box>
    </Box>
  )
}
export default Banner
