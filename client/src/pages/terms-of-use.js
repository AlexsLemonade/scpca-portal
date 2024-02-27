import React from 'react'
import { MarkdownPage } from 'components/MarkdownPage'
import { getLastUpdatedDate } from 'helpers/getLastUpdatedDate'
import termsOfUse from '../config/terms-of-use.md'

export const TermsOfUse = () => {
  const markdownContent = getLastUpdatedDate(
    termsOfUse,
    process.env.TOS_RELEASE
  )

  return <MarkdownPage markdown={markdownContent} />
}

export default TermsOfUse
