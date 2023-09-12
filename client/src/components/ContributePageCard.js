import React from 'react'
import { Box, Heading, Paragraph, Text } from 'grommet'
import { config } from 'config'
import { Button } from 'components/Button'
import { CardBandLarge } from 'components/Band'
import { WarningText } from 'components/WarningText'

export const ContributePageCard = () => {
  return (
    <CardBandLarge align="center" pad={{ top: 'large' }}>
      <Box margin={{ bottom: 'medium' }}>
        <WarningText
          iconColor="error"
          iconMargin="none"
          iconSize="24px"
          text={
            <Text color="error" size="24px" weight="bold">
              We are NOT currently accepting contributions
            </Text>
          }
        />
      </Box>
      <Box align="center" direction="row" gap="large" justify="between">
        <Box width={{ max: '680px' }}>
          <Heading level={5} margin={{ bottom: 'small' }} size="16px">
            Interested in contributing? Sign up to be notified.
          </Heading>
          <Paragraph>
            If you have an existing single-cell dataset you are interested in
            making available via the portal, please sign up to be notified about
            future opportunities. In the future, there will be a process for
            determining if your data meets the necessary requirements to be
            shared on the portal.
          </Paragraph>
        </Box>
        <Button
          href={config.links.contribute_hsform}
          label="Sign Up For Notifications"
          target="_blank"
          primary
        />
      </Box>
    </CardBandLarge>
  )
}

export default ContributePageCard
