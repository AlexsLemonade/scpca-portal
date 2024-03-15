import React from 'react'
import { MarkdownPage } from 'components/MarkdownPage'
import { LastUpdated } from 'components/LastUpdated'
import privacyPolicy from '../config/privacy-policy.md'

export const PrivacyPolicy = () => (
  <>
    <MarkdownPage markdown={privacyPolicy} />
    <LastUpdated date={process.env.PRIVACY_POLICY_RELEASE} />
  </>
)

export default PrivacyPolicy
