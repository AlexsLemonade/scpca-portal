import React from 'react'
import { Box, Button, Nav, Image, Paragraph, Text } from 'grommet'
import { Link } from 'components/Link'
import { FooterBand } from 'components/Band'
import { Icon } from 'components/Icon'
import { config } from 'config'

export const Footer = () => {
  return (
    <FooterBand elevation="medium" align="center" pad={{ vertical: 'xlarge' }}>
      <Box direction="row" justify="between" align="end" width="xlarge">
        <Box direction="row" justify="between" align="end" width="xlarge">
          <Box align="start" margin={{ vertical: 'large' }}>
            <Text color="black-tint-40">
              Alex’s Lemonade Stand Foundation for Childhood Cancer
            </Text>
            <Text color="black-tint-40">
              333 E. Lancaster Ave, #414, Wynnewood, PA 19096 USA
            </Text>
            <Text color="black-tint-40">
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
            pad={{ left: 'xlarge' }}
            margin={{ vertical: 'large' }}
          >
            <Box
              direction="row"
              gap="large"
              width={{ max: '220px' }}
              align="center"
            >
              <Box>
                <Paragraph textAlign="center" color="black-tint-40">
                  <Text size="small">Funded By</Text>
                </Paragraph>
                <Image src="/alsf-logo.png" />
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
                <Image src="/ccdl-logo.png" />
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
      <Box direction="row" justify="between" width="xlarge">
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
