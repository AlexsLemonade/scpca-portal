import React from 'react'
import { Box, Button, Heading, Paragraph } from 'grommet'
import { WarningCard } from 'components/WarningCard'
import { links } from 'config'

export const ContributePhaseOutBanner = () => (
  <WarningCard label="We are NOT currently accepting contributions">
    <Box
      align="center"
      direction="row"
      gap="large"
      justify="between"
      pad={{ horizontal: 'small', bottom: 'xlarge' }}
    >
      <Box width={{ max: '750px' }}>
        <Heading level={5} margin={{ bottom: 'small' }} size="16px">
          Interested in contributing? Sign up to be notified.
        </Heading>
        <Paragraph>
          If you have an existing single-cell dataset you are interested in
          making available via the portal, please sign up to be notified about
          future opportunities. In the future, there will be a process for
          determining if your data meets the necessary requirements to be shared
          on the portal.
        </Paragraph>
      </Box>
      <Button
        href={links.contributeHsForm}
        label="Sign Up For Notifications"
        target="_blank"
        primary
      />
    </Box>
  </WarningCard>
)

export default ContributePhaseOutBanner
