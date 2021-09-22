import React from 'react'
import { Box, Main } from 'grommet'
import { Header } from 'components/Header'

export const Layout = ({ children }) => {
  return (
    <Box height={{ min: '100vh' }}>
      <Box gridArea="header" margin={{ bottom: 'xlarge' }}>
        <Header />
      </Box>
      <Main width="xlarge" alignSelf="center" overflow="visible" align="center">
        {children}
      </Main>
    </Box>
  )
}

export default Layout
