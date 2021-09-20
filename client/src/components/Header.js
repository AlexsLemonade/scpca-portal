import React from 'react'
import { Box, Header as GrommetHeader, Nav, ResponsiveContext } from 'grommet'
import styled from 'styled-components'
import { Link } from 'components/Link'
import Logo from 'components/Logo'

const FixedBox = styled(Box)`
  position: fixed;
  width: 100%;
  z-index: 1;
  box-shadow: 0px 2px 5px 5px #fdfdfd;
`

export const Header = ({ className }) => {
  const size = React.useContext(ResponsiveContext)
  return (
    <Box height="80px">
      <FixedBox background="white">
        <GrommetHeader
          className={className}
          background="brand"
          border={[{ size: 'medium', side: 'bottom', color: '#F3E502' }]}
          justify="center"
          margin={{ bottom: '2rem' }}
        >
          <Box
            direction="row"
            width={{ max: size === 'large' ? 'xxlarge' : 'full' }}
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
              <Link color="white" href="/search" label="Browse" />
              <Link
                color="white"
                href="https://help.resources.alexslemonade.org/knowledge"
                label="Docs"
              />
            </Nav>
          </Box>
        </GrommetHeader>
      </FixedBox>
    </Box>
  )
}

export default Header
