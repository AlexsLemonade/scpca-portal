import React from 'react'
import { MarkdownPage } from 'components/MarkdownPage'
import { LastUpdated } from 'components/LastUpdated'
import privacyPolicy from '../config/privacy-policy.md'

// TEMP: The Last Updated line is not commented out in this markdown, so temporarily adding this fix
// TODO: handle this with regex
const content = privacyPolicy.replace('Last Updated: 2021-11-03', '')

export const PrivacyPolicy = () => (
  <>
    <MarkdownPage markdown={content} />
    <LastUpdated date={process.env.PRIVACY_POLICY_RELEASE} />
  </>
)

export default PrivacyPolicy
