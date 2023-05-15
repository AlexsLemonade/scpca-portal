import React, { useState } from 'react'
import { useRouter } from 'next/router'
import { Box, Nav as GrommetNav } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { DonateButton } from 'components/DonateButton'
import { Link } from 'components/Link'
import { ResponsiveSheet } from 'components/ResponsiveSheet'
import { Menu } from 'grommet-icons'
import { config } from 'config'

export const Nav = ({ donate = false }) => {
  const router = useRouter()
  const { size, responsive } = useResponsive()
  const linksColor = responsive('brand', 'white')
  const [showMenu, setShowMenu] = useState(false)
  // show donate button on about page only
  const donatePaths = ['/about']
  const showDonate = donatePaths.includes(router.pathname)

  return (
    <Box direction="row" gap={responsive('small', 'xlarge')}>
      {size === 'small' && (
        <GrommetNav>{donate && <DonateButton yellow />}</GrommetNav>
      )}
      <ResponsiveSheet
        label={<Menu />}
        show={showMenu}
        setShow={setShowMenu}
        alignSelf="center"
      >
        <GrommetNav
          direction={responsive('column', 'row')}
          gap="xlarge"
          align={responsive('start', 'center')}
          width={responsive({ min: '300px' })}
        >
          <Link color={linksColor} href="/" label="Home" />
          <Link color={linksColor} href="/about" label="About" />
          <Link color={linksColor} href="/projects" label="Browse" />
          <Link color={linksColor} href={config.links.help} label="Docs" />
          <Link color={linksColor} href="/contribute" label="Contribute" />
        </GrommetNav>
      </ResponsiveSheet>
      {size !== 'small' && (
        <GrommetNav>{showDonate && <DonateButton yellow />}</GrommetNav>
      )}
    </Box>
  )
}

export default Nav
