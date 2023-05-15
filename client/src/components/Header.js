import React from 'react'
import { Box, Header as GrommetHeader } from 'grommet'
import { Link } from 'components/Link'
import { Logo } from 'components/Logo'
import { Nav } from 'components/Nav'
import { ProgressBar } from 'components/ProgressBar'

export const Header = () => (
  <GrommetHeader background="brand" justify="center" pad={{ bottom: 'small' }}>
    <Box
      direction="row"
      width={{ max: 'xlarge' }}
      fill="horizontal"
      justify="between"
      align="center"
    >
      <Box direction="row" align="center" gap="small">
        <Link href="/">
          <Logo />
        </Link>
      </Box>
      <Nav />
    </Box>
    <ProgressBar />
  </GrommetHeader>
)

export default Header
