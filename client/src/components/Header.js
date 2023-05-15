import React from 'react'
import { Box, Header as GrommetHeader } from 'grommet'
import { Link } from 'components/Link'
import Logo from 'components/Logo'
import { Nav } from 'components/Nav'

export const Header = ({ className, margin }) => (
  <GrommetHeader
    className={className}
    background="brand"
    justify="center"
    margin={margin}
  >
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
  </GrommetHeader>
)

export default Header
