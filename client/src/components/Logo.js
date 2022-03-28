import React, { useState, useEffect } from 'react'
import { Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import styled from 'styled-components'
import ASLFLogo from '../images/alsf-logo.svg'
import ALSFLogoBlue from '../images/alsf-logo-blue.svg'

const ALSFLogoBlueStyled = styled(ALSFLogoBlue)``

const Logo = () => {
  const { size, responsive } = useResponsive()
  const [scrolled, setScrolled] = useState(false)
  const width = responsive('60px', '91px')
  const small = size === 'small'
  const showScrolled = scrolled || small

  const height = showScrolled ? '74px' : '112px'
  const background = showScrolled ? 'alexs-lemonade' : 'transparent'

  useEffect(() => {
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
      direction="row"
      align="start"
      justify="center"
      gap="small"
      overflow="visible"
      height="74px"
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
      <Box height="74px" align="center" justify="center">
        <Text serif size={responsive('medium', 'large')} color="white">
          ScPCA Portal
        </Text>
      </Box>
    </Box>
  )
}

export default Logo
