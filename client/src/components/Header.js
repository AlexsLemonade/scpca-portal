import React from 'react'
import { Box, Header as GrommetHeader, Nav } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { DonateButton } from 'components/DonateButton'
import { Link } from 'components/Link'
import Logo from 'components/Logo'
import { ResponsiveSheet } from 'components/ResponsiveSheet'
import { Menu } from 'grommet-icons'
import { config } from 'config'

export const Header = ({ className, margin, donate = false }) => {
  const { size, responsive } = useResponsive()
  const linksColor = responsive('brand', 'white')
  const [showMenu, setShowMenu] = React.useState(false)

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
        align="center"
      >
        <Box direction="row" align="center" gap="small">
          <Link href="/">
            <Logo />
          </Link>
        </Box>
        <Box direction="row" gap={responsive('small', 'xlarge')}>
          {size === 'small' && <Nav>{donate && <DonateButton yellow />}</Nav>}
          <ResponsiveSheet
            label={<Menu />}
            show={showMenu}
            setShow={setShowMenu}
            alignSelf="center"
          >
            <Nav
              direction={responsive('column', 'row')}
              gap="xlarge"
              align={responsive('start', 'center')}
              width={responsive({ min: '300px' })}
            >
              <Link color={linksColor} href="/" label="Home" />
              <Link color={linksColor} href="/about" label="About" />
              <Link color={linksColor} href="/projects" label="Browse" />
              <Link color={linksColor} href={config.links.help} label="Docs" />
            </Nav>
          </ResponsiveSheet>
          {size !== 'small' && <Nav>{donate && <DonateButton yellow />}</Nav>}
        </Box>
      </Box>
    </GrommetHeader>
  )
}

export default Header
