import React from 'react'
import { Box, Paragraph, Text, Markdown } from 'grommet'
import styled from 'styled-components'

const StyledLi = styled(Box)`
  list-style: revert;
  padding-left: 20px;
`

const StyledOl = styled(Box)`
  list-style: revert;
`

const StyledUl = styled(Box)`
  list-style: revert;
`

export const MarkdownPage = ({ markdown }) => {
  const components = {
    p: { component: Paragraph, props: { margin: { bottom: 'medium' } } },
    strong: { component: Text, props: { weight: 'bold' } },
    ol: { component: StyledOl, props: { as: 'ol' } },
    ul: { component: StyledUl, props: { as: 'ul' } },
    li: { component: StyledLi, props: { as: 'li' } }
  }

  if (!markdown) return 'missing'
  return (
    <Box pad={{ vertical: 'large' }} justify="center">
      <Box width="large">
        <Markdown components={components}>{markdown}</Markdown>
      </Box>
    </Box>
  )
}

export default MarkdownPage