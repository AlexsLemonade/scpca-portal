import React from 'react'
import { MarkdownPage } from 'components/MarkdownPage'
import { LastUpdated } from 'components/MarkdownLastUpdated'
import termsOfUse from '../config/terms-of-use.md'

export const TermsOfUse = () => (
  <>
    <MarkdownPage markdown={termsOfUse} />
    <LastUpdated date={process.env.TOS_RELEASE} />
  </>
)

export default TermsOfUse
