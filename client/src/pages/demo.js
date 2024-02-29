import React from 'react'
import { Box, Heading } from 'grommet'
import { config } from 'config'
import { Link } from 'components/Link'

export const Demo = () => {
  const termsOfUseRoute = Object.keys(config.termsOfUse)
  const privacyPolicyRoute = Object.keys(config.privacyPolicy)

  return (
    <Box gap="xlarge" margin={{ bottom: 'xlarge' }}>
      <Box direction="row" gap="xlarge">
        <Heading level={4}>Terms of use:</Heading>
        <Box>
          <Heading level={5}>A single link:</Heading>
          <Link
            label={config.termsOfUse.accessToAndUseOfContent.label}
            href={config.termsOfUse.accessToAndUseOfContent.path}
          />
        </Box>
        <Box>
          <Heading level={5}>All available links:</Heading>
          {termsOfUseRoute.map((k) => (
            <Link
              key={k}
              label={config.termsOfUse[k].label}
              href={config.termsOfUse[k].path}
            />
          ))}
        </Box>
      </Box>
      <Box direction="row" gap="xlarge">
        <Heading level={4}>Terms of use:</Heading>
        <Box>
          <Heading level={5}>A single link:</Heading>
          <Link
            label={
              config.privacyPolicy.mayWeUseCookiesOrOtherTrackingTools.label
            }
            href={config.privacyPolicy.mayWeUseCookiesOrOtherTrackingTools.path}
          />
        </Box>
        <Box>
          <Heading level={5}>All available links:</Heading>
          {privacyPolicyRoute.map((k) => (
            <Link
              key={k}
              label={config.privacyPolicy[k].label}
              href={config.privacyPolicy[k].path}
            />
          ))}
        </Box>
      </Box>
    </Box>
  )
}

export default Demo
