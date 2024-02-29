import React from 'react'
import { MarkdownPage } from 'components/MarkdownPage'
import { MarkdownLastUpdatedDate } from 'components/MarkdownLastUpdated'
import privacyPolicy from '../config/privacy-policy.md'

export const PrivacyPolicy = () => (
  <>
    <MarkdownPage markdown={privacyPolicy} />
    <MarkdownLastUpdatedDate env={process.env.PRIVACY_POLICY_RELEASE} />
  </>
)

export default PrivacyPolicy
