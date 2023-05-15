import React, { useCallback, useRef, useState } from 'react'
import { useRouter } from 'next/router'
import { useResizeObserver } from 'hooks/useResizeObserver'
import { Box, Main } from 'grommet'
import { ContributeBanner } from 'components/ContributeBanner'
import { Footer } from 'components/Footer'
import { Header } from 'components/Header'
import styled, { css } from 'styled-components'

const StickyBox = styled(Box)`
  position: sticky;
  top: 0;
  left: 0;
  z-index: 100;
  ${({ boxShadow }) =>
    boxShadow &&
    css`
      box-shadow: 0px 2px 5px 5px #fdfdfd;
    `}
`

export const Layout = ({ children }) => {
  const router = useRouter()

  // get the height of the wrapper for the hero banner (e.g. ContributeBanner)
  const wrapperRef = useRef(null)
  const [wrapperHeight, setWrapperHeights] = useState(0)
  useResizeObserver(
    wrapperRef,
    useCallback((ref) => {
      setWrapperHeights(ref.clientHeight)
    }, [])
  )

  // exclude css rules (padding /box shadow) on the following pages
  const excludedPages = ['/', '/about']
  const isExcludedPages = excludedPages.includes(router.pathname)
  const isBoxShadow = !isExcludedPages && wrapperHeight === 0

  // add the top margin & box shadow to the following pages when the contribution banner is hidden
  const projectPages = ['/projects', '/projects/[scpca_id]']
  const isProjectPages =
    projectPages.includes(router.pathname) && wrapperHeight === 0

  return (
    <Box height={{ min: '100vh' }}>
      <StickyBox boxShadow={isBoxShadow}>
        <Header />
      </StickyBox>
      <Box ref={wrapperRef}>
        <ContributeBanner />
      </Box>
      <Main
        align="center"
        alignSelf="center"
        justify="center"
        overflow="visible"
        margin={{ top: isProjectPages ? 'xlarge' : '' }}
        pad={{ top: !isExcludedPages ? 'xlarge' : '' }}
        width={isExcludedPages ? 'full' : 'xlarge'}
      >
        {children}
      </Main>
      <Footer />
    </Box>
  )
}

export default Layout
