import React from 'react'
import { Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import styled from 'styled-components'
import ASLFLogo from '../images/alsf-logo.svg'
import ALSFLogoBlue from '../images/alsf-logo-blue.svg'

const ALSFLogoBlueStyled = styled(ALSFLogoBlue)``

const Logo = () => {
  const { size, responsive } = useResponsive()
  const [scrolled, setScrolled] = React.useState(false)
  const width = responsive('60px', '91px')
  const small = size === 'small'
  const showScrolled = scrolled || small

  const margin = showScrolled ? 0 : 38
  const height = showScrolled ? '74px' : '112px'
  const background = showScrolled ? 'alexs-lemonade' : 'transparent'

  React.useEffect(() => {
    const handleScroll = () => {
      if (window.pageYOffset > 0 && !scrolled) setScrolled(true)
      if (window.pageYOffset === 0 && scrolled) setScrolled(false)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })

    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  })

  return (
    <Box
      height="full"
      direction="row"
      align="center"
      gap="small"
      margin={{ bottom: `-${margin}px` }}
    >
      <Box
        width={width}
        height={height}
        justify="center"
        background={background}
      >
        {showScrolled ? (
          <Box pad="small">
            <ALSFLogoBlueStyled />
          </Box>
        ) : (
          <ASLFLogo />
        )}
      </Box>
      <Text
        serif
        size={responsive('medium', 'large')}
        color="white"
        margin={{ bottom: `${margin}px` }}
      >
        ScPCA Portal
      </Text>
    </Box>
  )
}

export default Logo
