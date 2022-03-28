import React from 'react'
import { Box, Button, Nav, Image, Paragraph, Text } from 'grommet'
import { Link } from 'components/Link'
import { FooterBand } from 'components/Band'
import { Icon } from 'components/Icon'
import { config } from 'config'
import { useResponsive } from 'hooks'
import styled from 'styled-components'

const FooterImage = styled(Image)`
  max-width: 100%;
  max-height: 100%;
`

export const Footer = () => {
  const { responsive } = useResponsive()

  const direction = responsive('column', 'row')

  return (
    <FooterBand
      elevation="medium"
      align="center"
      justify="center"
      pad={{ vertical: 'xlarge' }}
    >
      <Box direction={direction} justify="between" align="end" width="xlarge">
        <Box
          direction={direction}
          justify="between"
          align={responsive('center', 'end')}
          width="xlarge"
        >
          <Box
            margin={{ vertical: 'large' }}
            align={responsive('center', 'start')}
          >
            <Text size={responsive('small', 'medium')} color="black-tint-40">
              Alex’s Lemonade Stand Foundation for Childhood Cancer
            </Text>
            <Text size={responsive('small', 'medium')} color="black-tint-40">
              333 E. Lancaster Ave, #414, Wynnewood, PA 19096 USA
            </Text>
            <Text size={responsive('small', 'medium')} color="black-tint-40">
              Phone: 866.333.1213 • Fax: 610.649.3038
            </Text>
            <Box margin={{ top: 'large' }}>
              <Button
                primary
                label="Donate"
                href={config.links.donate}
                target="_blank"
              />
            </Box>
          </Box>
          <Box
            basis="1/3"
            pad={responsive({ bottom: 'large' }, { left: 'xlarge' })}
            margin={{ vertical: 'large' }}
          >
            <Box
              direction="row"
              gap={responsive('xxlarge', 'xlarge')}
              width={{ width: 'full', max: '220px' }}
              align="center"
              justify="center"
            >
              <Box align="center">
                <Paragraph textAlign="center" color="black-tint-40">
                  <Text size="small">Funded By</Text>
                </Paragraph>
                <Box
                  pad={{ top: 'small' }}
                  height="60px"
                  width={{ width: 'full', max: '50px' }}
                >
                  <FooterImage src="/alsf-logo.png" />
                </Box>

                <Box
                  direction="row"
                  pad={{ top: 'medium' }}
                  gap="medium"
                  justify="center"
                  align="center"
                >
                  <Link href={config.links.alsfTwitter}>
                    <Icon name="Twitter" color="black-tint-40" />
                  </Link>
                  <Link href={config.links.alsfInstagram}>
                    <Icon name="Instagram" color="black-tint-40" />
                  </Link>
                  <Link href={config.links.alsfFacebook}>
                    <Icon name="Facebook" color="black-tint-40" />
                  </Link>
                </Box>
              </Box>
              <Box>
                <Paragraph textAlign="center" color="black-tint-40">
                  <Text size="small">Developed By</Text>
                </Paragraph>
                <Box
                  pad={{ top: 'small' }}
                  height="60px"
                  width={{ width: 'full', max: '100px' }}
                >
                  <FooterImage src="/ccdl-logo.png" />
                </Box>
                <Box
                  direction="row"
                  pad={{ top: 'medium' }}
                  gap="medium"
                  justify="center"
                  align="center"
                >
                  <Link href={config.links.ccdlGithub}>
                    <Icon name="Github" color="black-tint-40" />
                  </Link>
                  <Link href={config.links.ccdlTwitter}>
                    <Icon name="Twitter" color="black-tint-40" />
                  </Link>
                </Box>
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>
      <Box
        direction="row"
        justify={responsive('around', 'between')}
        width="xlarge"
      >
        <Box>
          <Nav direction="row" align="center" gap="large">
            <Link href="/terms-of-use" label="Terms of Use" />
            <Link href="/privacy-policy" label="Privacy Policy" />
            <Link href={config.links.help} label="Docs" />
          </Nav>
        </Box>
      </Box>
    </FooterBand>
  )
}

export default Footer
