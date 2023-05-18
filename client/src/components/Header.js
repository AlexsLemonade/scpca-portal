import React from 'react'
import { useRouter } from 'next/router'
import { Box, Header as GrommetHeader } from 'grommet'
import { Link } from 'components/Link'
import { Logo } from 'components/Logo'
import { Nav } from 'components/Nav'
import { PageLoader } from 'components/PageLoader'

export const Header = () => {
  const router = useRouter()

  return (
    <GrommetHeader
      background="brand"
      justify="center"
      direction="column"
      gap="small"
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
        <Nav router={router} />
      </Box>
      <PageLoader router={router} />
    </GrommetHeader>
  )
}

export default Header
