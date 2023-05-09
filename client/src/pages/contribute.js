import React from 'react'
import { MarkdownPage } from 'components/MarkdownPage'
import contributionGuidelines from '../config/contribution-guidelines.md'

export const Contribute = () => (
  <MarkdownPage markdown={contributionGuidelines} />
)

export default Contribute
