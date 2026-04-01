import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box } from 'grommet'
import { MarkdownPage } from 'components/MarkdownPage'
import { LastUpdated } from 'components/LastUpdated'
import privacyPolicy from '../config/privacy-policy.md'

// TEMP: The Last Updated line is not commented out in this markdown, so temporarily adding this fix
// TODO: handle this with regex
const content = privacyPolicy.replace('Last Updated: 2021-11-03', '')

export const PrivacyPolicy = () => {
  const { responsive } = useResponsive()

  return (
    <Box
      pad={{
        horizontal: responsive('medium', null, 'medium')
      }}
    >
      <MarkdownPage markdown={content} />
      <LastUpdated date={process.env.PRIVACY_POLICY_RELEASE} />
    </Box>
  )
}

export default PrivacyPolicy
