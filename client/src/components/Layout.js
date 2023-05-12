import React, { useRef, useState, useCallback } from 'react'
import { useRouter } from 'next/router'
import { useBanner } from 'hooks/useBanner'
import { useResizeObserver } from 'hooks/useResizeObserver'
import { Box, Main } from 'grommet'
import { ContributeBanner } from 'components/ContributeBanner'
import { Footer } from 'components/Footer'
import { Header } from 'components/Header'
import { PageLoader } from 'components/PageLoader'
import { RecruitNFBanner } from 'components/RecruitNFBanner'
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
  const router = useRouter()
  const { banner } = useBanner()

  // get the height of FixedBox for to preserve the margin
  const [fixedBoxHeight, setFixedBoxHeight] = useState(0)
  const fixedBoxRef = useRef(null)
  useResizeObserver(
    fixedBoxRef,
    useCallback((ref) => {
      setFixedBoxHeight(`${ref.clientHeight}px`)
    }, [])
  )

  // donate button on about page only
  const donatePaths = ['/about']
  const showDonate = donatePaths.includes(router.pathname)

  // homepage is full width
  const widePaths = ['/', '/about']
  const showWide = widePaths.includes(router.pathname)

  // exclude the padding / and box shadow on the following pages
  const excludPadPaths = ['/', '/about']
  const showMargin = !excludPadPaths.includes(router.pathname)

  // add the top margin to the following pages when the contribution banner is hidden
  const addTopMarginPaths = ['/projects', '/projects/[scpca_id]']
  const addTopMargin =
    addTopMarginPaths.includes(router.pathname) &&
    showMargin &&
    !banner['contribute-banner']

  // exclude the contribue banner on the following pages
  const excludeContributeBanner = [
    '/contribute',
    '/privacy-policy',
    '/terms-of-use'
  ]
  const showContributeBanner = !excludeContributeBanner.includes(
    router.pathname
  )

  return (
    <Box height={{ min: '100vh' }}>
      <Box height={fixedBoxHeight}>
        <FixedBox background="white" ref={fixedBoxRef} showMargin={showMargin}>
          <RecruitNFBanner hidden />
          <Header margin={{ bottom: 'small' }} donate={showDonate} />
          <ProgressBar />
        </FixedBox>
      </Box>
      {showContributeBanner && <ContributeBanner />}
      <Main
        width={showWide ? 'full' : 'xlarge'}
        alignSelf="center"
        overflow="visible"
        align="center"
        justify="center"
        margin={{ top: addTopMargin ? 'xlarge' : '' }}
        pad={{ top: showMargin ? 'xlarge' : '' }}
      >
        {children}
      </Main>
      <Footer />
    </Box>
  )
}

export default Layout
