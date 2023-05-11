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
  fullWidth = true,
  showByDefault = true,
  children
}) => {
  const { banner, hideBanner, openBanner } = useBanner()

  useEffect(() => {
    if (showByDefault) openBanner(id)
  }, [])

  if (!banner[id]) return null

  return (
    <Box
      background={background}
      direction="row"
      justify="center"
      width="100%"
      elevation={elevation}
      style={{ zIndex: 1 }}
    >
      <Box
        direction="row"
        justify="center"
        width={fullWidth ? '100%' : 'xlarge'}
      >
        {children}
        <Box
          pad={{ vertical: 'medium', right: '24px' }}
          onClick={() => hideBanner(id)}
        >
          <Icon name="Cross" color={closeIconColor} size="16px" />
        </Box>
      </Box>
    </Box>
  )
}
export default Banner
