import React, { useCallback, useRef, useState } from 'react'
import { useRouter } from 'next/router'
import { useResizeObserver } from 'hooks/useResizeObserver'
import { Box, Main } from 'grommet'
import { ContributeBanner } from 'components/ContributeBanner'
import { Footer } from 'components/Footer'
import { Header } from 'components/Header'
import styled from 'styled-components'

const StickyBox = styled(Box)`
  position: sticky;
  top: 0;
  left: 0;
  z-index: 100;
`

export const Layout = ({ children }) => {
  const router = useRouter()

  // check whether the scrollable hero area contains any child elements (e.g. ContributeBanner)
  const scrollableHeroRef = useRef(null)
  const [isElement, setIsElement] = useState(0)
  useResizeObserver(
    scrollableHeroRef,
    useCallback((ref) => {
      setIsElement(ref.clientHeight > 0)
    }, [])
  )

  const excludedPages = ['/', '/about']
  const isExcludedPages = excludedPages.includes(router.pathname)
  // apply the box shadow to StickyBox on the non-excluded pages when no scrollable hero element
  const isBoxShadow = !isExcludedPages && !isElement

  // add the top margin & box shadow to the project pages when no scrollable hero element
  const projectPages = ['/projects', '/projects/[scpca_id]']
  const isProjectPages = projectPages.includes(router.pathname) && !isElement

  return (
    <Box height={{ min: '100vh' }}>
      <StickyBox elevation={isBoxShadow ? 'xlarge' : ''}>
        <Header />
      </StickyBox>
      <Box ref={scrollableHeroRef}>
        {/* scrollable hero area */}
        <ContributeBanner />
      </Box>
      <Main margin={{ top: isProjectPages ? 'xlarge' : '' }}>{children}</Main>
      <Footer />
    </Box>
  )
}

export default Layout
