import React from 'react'
import { Box } from 'grommet'
import styled from 'styled-components'
import { MarkdownPage } from 'components/MarkdownPage'
import { LastUpdated } from 'components/LastUpdated'
import termsOfUse from '../config/terms-of-use.md'

// terms-of-use.md file has a sublist that is not handled gracefully,
// This override removes the bullets on the sublist in section 3.
const StyledList = styled(Box)`
  list-style: none;
`

export const TermsOfUse = () => {
  const components = {
    ul: { component: StyledList, props: { as: 'ul' } }
    // li: { component: StyledLi, props: { as: "li" } },
  }
  return (
    <>
      <MarkdownPage components={components} markdown={termsOfUse} />
      <LastUpdated date={process.env.TOS_RELEASE} />
    </>
  )
}

export default TermsOfUse
