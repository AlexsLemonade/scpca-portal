import React from 'react'
import { Box, Paragraph, Text, Markdown } from 'grommet'
import { FixedContainer } from 'components/FixedContainer'
import styled from 'styled-components'

const StyledLi = styled(Box)`
  list-style: revert;
  padding-left: 20px;
`

const StyledList = styled(Box)`
  list-style: revert;
`

export const MarkdownPage = ({
  components = {},
  markdown,
  width = 'large'
}) => {
  const config = {
    p: { component: Paragraph, props: { margin: { bottom: 'medium' } } },
    strong: { component: Text, props: { weight: 'bold' } },
    ol: { component: StyledList, props: { as: 'ol' } },
    ul: { component: StyledList, props: { as: 'ul' } },
    li: { component: StyledLi, props: { as: 'li' } },
    ...components
  }

  if (!markdown) return 'missing'

  return (
    <FixedContainer align="center">
      <Box pad={{ vertical: 'large' }} justify="center">
        <Box width={width}>
          <Markdown components={config}>{markdown}</Markdown>
        </Box>
      </Box>
    </FixedContainer>
  )
}

export default MarkdownPage
