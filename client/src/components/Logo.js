import React from 'react'
import { Box, Text } from 'grommet'
import ASLFLogo from '../images/alsf-logo.svg'
import ALSFLogoBlue from '../images/alsf-logo-blue.svg'

const Logo = () => {
  const [scrolled, setScrolled] = React.useState(false)
  const margin = scrolled ? 0 : 38
  const height = scrolled ? '74px' : '112px'
  const background = scrolled ? 'alexs-lemonade' : 'transparent'

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
        width="91px"
        height={height}
        justify="center"
        background={background}
      >
        {scrolled ? (
          <Box pad="small">
            <ALSFLogoBlue margin={{ top: '38px' }} pad="small" />
          </Box>
        ) : (
          <ASLFLogo />
        )}
      </Box>
      <Text serif size="large" color="white" margin={{ bottom: `${margin}px` }}>
        ScPCA Portal
      </Text>
    </Box>
  )
}

export default Logo
