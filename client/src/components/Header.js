import React from 'react'
import { Box, Header as GrommetHeader, Nav, ResponsiveContext } from 'grommet'
import { DonateButton } from 'components/DonateButton'
import { Link } from 'components/Link'
import Logo from 'components/Logo'

export const Header = ({ className, margin, donate = false }) => {
  const size = React.useContext(ResponsiveContext)
  return (
    <GrommetHeader
      className={className}
      background="brand"
      border={[{ size: 'medium', side: 'bottom', color: '#F3E502' }]}
      justify="center"
      margin={margin}
    >
      <Box
        direction="row"
        width={{ max: 'xlarge' }}
        fill="horizontal"
        justify="between"
      >
        <Box direction="row" align="center" gap="small">
          <Link href="/">
            <Logo />
          </Link>
        </Box>
        <Nav
          direction="row"
          gap={size === 'large' ? 'xlarge' : 'medium'}
          align="center"
        >
          <Link color="white" href="/" label="Home" />
          <Link color="white" href="/about" label="About" />
          <Link color="white" href="/projects" label="Browse" />
          <Link color="white" href="https://alexslemonade.org" label="Docs" />
          {donate && <DonateButton />}
        </Nav>
      </Box>
    </GrommetHeader>
  )
}

export default Header
