import React, { useRef } from 'react'
import { Box, Paragraph, Text, Markdown } from 'grommet'
import styled from 'styled-components'
import Error from 'pages/_error'
import { useScrollToTextContentHash } from 'hooks/useScrollToTextContentHash'

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
  const markdownRef = useRef()

  useScrollToTextContentHash(
    markdownRef,
    'ol > li > p:first-child > span:first-child'
  )

  const markdownConfig = {
    p: { component: Paragraph, props: { margin: { bottom: 'medium' } } },
    strong: { component: Text, props: { weight: 'bold' } },
    ol: { component: StyledList, props: { as: 'ol' } },
    ul: { component: StyledList, props: { as: 'ul' } },
    li: { component: StyledLi, props: { as: 'li' } },
    ...components
  }

  if (!markdown) return <Error />

  return (
    <Box pad={{ vertical: 'large' }} justify="center">
      <Box width={width}>
        <Markdown ref={markdownRef} components={markdownConfig}>
          {markdown}
        </Markdown>
      </Box>
    </Box>
  )
}

export default MarkdownPage
