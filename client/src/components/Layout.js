import React, { useRef, useState, useCallback } from 'react'
import { useRouter } from 'next/router'
// import { useBanner } from 'hooks/useBanner'
import { useNotification } from 'hooks/useNotification'
import { useResizeObserver } from 'hooks/useResizeObserver'
import { Box, Main } from 'grommet'
import { ContributeBanner } from 'components/ContributeBanner'
import { EnvarBanner } from 'components/EnvarBanner'
import { Footer } from 'components/Footer'
import { Header } from 'components/Header'
import { Notifications } from 'components/Notifications'
import { PageLoader } from 'components/PageLoader'
import styled from 'styled-components'

const FixedBox = styled(Box)`
  position: fixed;
  width: 100%;
  z-index: 3;
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
  const { notifications } = useNotification()

  // get the height of FixedBox for to preserve the margin
  const [fixedBoxHeight, setFixedBoxHeight] = useState('0px')
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
  const widePaths = ['/', '/about', '/portal-wide']
  const showWide = widePaths.includes(router.pathname)

  // exclude the contribue banner on the following pages
  const excludeContributeBanner = [
    '/contribute',
    '/privacy-policy',
    '/terms-of-use'
  ]

  const isContributeOpen = process.env.CONTRIBUTIONS_OPEN === 'ON'

  // show the contributeBanner
  const showContributeBanner =
    isContributeOpen && !excludeContributeBanner.includes(router.pathname)

  const showEnvarBanner = process.env.BANNER_STATE === 'ON'

  const width = showWide ? 'full' : 'xlarge'

  return (
    <Box height={{ min: '100vh' }}>
      <Box height={fixedBoxHeight}>
        <FixedBox background="white" ref={fixedBoxRef}>
          {notifications.length > 0 && <Notifications />}
          {showEnvarBanner && <EnvarBanner width={width} />}
          <Header margin={{ bottom: 'small' }} donate={showDonate} />
          <ProgressBar />
        </FixedBox>
      </Box>
      {showContributeBanner && <ContributeBanner width={width} />}
      <Main
        width={showWide ? 'full' : 'xlarge'}
        alignSelf="center"
        overflow="visible"
        align="center"
        justify="center"
        pad={{ top: showWide ? '' : 'xlarge' }}
      >
        {children}
      </Main>
      <Footer />
    </Box>
  )
}

export default Layout
