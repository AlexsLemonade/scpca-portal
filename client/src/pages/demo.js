import React from 'react'
import { Box, Heading } from 'grommet'
import { config } from 'config'
import getMarkdownLink from 'helpers/getMarkdownLink'
import { Link } from 'components/Link'

export const Demo = () => {
  // route can be obtained from the page URL
  // e.g. ) refine.bio/terms-of-use
  const termsOfUseRoute = 'terms-of-use'
  const privacyPolicy = 'privacy-policy'
  return (
    <Box>
      <Heading level={3}>Available linked sections in markdown pages:</Heading>
      <Box direction="row" gap="xlarge">
        <Box>
          <Heading level={5}>Terms of use</Heading>
          {config.markdownLinkable[termsOfUseRoute].map((x) => (
            <Link
              key={x}
              label={x}
              href={getMarkdownLink(termsOfUseRoute, x)}
            />
          ))}
        </Box>
        <Box>
          <Heading level={5}>Privacy Policy</Heading>
          {config.markdownLinkable[privacyPolicy].map((x) => (
            <Link key={x} label={x} href={getMarkdownLink(privacyPolicy, x)} />
          ))}
        </Box>
      </Box>
    </Box>
  )
}

export default Demo
