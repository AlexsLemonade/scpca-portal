import React from 'react'
import { useRouter } from 'next/router'
import { Box, Main } from 'grommet'
import { Header } from 'components/Header'
import { Footer } from 'components/Footer'
import styled, { css } from 'styled-components'

const FixedBox = styled(Box)`
  position: fixed;
  width: 100%;
  z-index: 3;
  ${({ showMargin }) =>
    showMargin &&
    css`
      box-shadow: 0px 2px 5px 5px #fdfdfd;
    `}
`
export const Layout = ({ children }) => {
  const router = useRouter()

  // donate button on about page only
  const donatePaths = ['/about']
  const showDonate = donatePaths.includes(router.pathname)

  // homepage is full width
  const widePaths = ['/', '/about']
  const showWide = widePaths.includes(router.pathname)

  // exclude margin / and box shadow on homepage
  const excludeMarginPaths = ['/', '/about']
  const showMargin = !excludeMarginPaths.includes(router.pathname)

  return (
    <Box height={{ min: '100vh' }}>
      <Box margin={showMargin ? { bottom: 'xlarge' } : ''}>
        <Box height="80px">
          <FixedBox showMargin={showMargin} background="white">
            <Header
              margin={showMargin ? { bottom: '12px' } : ''}
              donate={showDonate}
            />
          </FixedBox>
        </Box>
      </Box>
      <Main
        width={showWide ? 'full' : 'xlarge'}
        alignSelf="center"
        overflow="visible"
        align="center"
        justify="center"
      >
        {children}
      </Main>
      <Footer />
    </Box>
  )
}

export default Layout
