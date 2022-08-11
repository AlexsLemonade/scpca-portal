import React from 'react'
import { useBanner } from 'hooks/useBanner'
import { useRouter } from 'next/router'
import { Box, Main } from 'grommet'
import { Banner } from 'components/Banner'
import { Footer } from 'components/Footer'
import { Header } from 'components/Header'
import { PageLoader } from 'components/PageLoader'
import { config } from 'config'
import styled, { css } from 'styled-components'

const FixedBox = styled(Box)`
  position: fixed;
  width: 100%;
  z-index: 3;
  // padding-bottom: 8px;
  ${({ showMargin }) =>
    showMargin &&
    css`
      box-shadow: 0px 2px 5px 5px #fdfdfd;
    `}
`

const ProgressBar = styled(PageLoader)`
  position: absolute;
  top: 100%;
  width: 100%;
  z-index: -1;
  transform: translate(0, -100%);
  height: 12px;
`

export const Layout = ({ children }) => {
  const { bannerHeight } = useBanner()
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
        <Box height={`${80 + bannerHeight}px`}>
          <FixedBox showMargin={showMargin} background="white">
            <Banner
              background="alexs-lemonade-tint-40"
              color="black"
              ctaLink={config.links.recruitment_hsform}
              ctaLabel="Sign up to test our pipeline"
              label="Processing your own single-cell data?"
              iconName="htmlGear"
            />
            <Header margin={{ bottom: 'small' }} donate={showDonate} />
            <ProgressBar />
          </FixedBox>
        </Box>
      </Box>
      <Main
        width={showWide ? 'full' : 'xlarge'}
        alignSelf="center"
        overflow="visible"
        align="center"
        justify="center"
        pad={showMargin ? { top: 'xlarge' } : {}}
      >
        {children}
      </Main>
      <Footer />
    </Box>
  )
}

export default Layout
