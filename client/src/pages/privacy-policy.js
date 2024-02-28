import React from 'react'
import { MarkdownPage } from 'components/MarkdownPage'
import { getLastUpdatedDate } from 'helpers/getLastUpdatedDate'
import privacyPolicy from '../config/privacy-policy.md'

export const PrivacyPolicy = () => {
  const markdownContent = getLastUpdatedDate(
    privacyPolicy,
    process.env.PRIVACY_POLICY_RELEASE
  )

  return <MarkdownPage markdown={markdownContent} />
}

export default PrivacyPolicy
