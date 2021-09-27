import React from 'react'
import { useRouter } from 'next/router'
import { Box, Main } from 'grommet'
import { Header } from 'components/Header'

export const Layout = ({ children }) => {
  const router = useRouter()
  const donatePaths = ['/about']
  const showDonate = donatePaths.includes(router.pathname)
  return (
    <Box height={{ min: '100vh' }}>
      <Box margin={{ bottom: 'xlarge' }}>
        <Header donate={showDonate} />
      </Box>
      <Main width="xlarge" alignSelf="center" overflow="visible" align="center">
        {children}
      </Main>
    </Box>
  )
}

export default Layout
