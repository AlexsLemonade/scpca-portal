import React, { useEffect, useState } from 'react'
import { Box, Paragraph, Text, Markdown } from 'grommet'
import styled from 'styled-components'
import formatStringToIdName from 'helpers/formatStringToIdName'
import getHash from 'helpers/getHash'

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
  const sectionId = getHash()
  const [offset, setOffset] = useState(0)

  useEffect(() => {
    const sections = document.querySelectorAll(
      'ol > li > p:first-child > span:first-child'
    )
    // we can use this to generate a list of linkable section text node for the config
    // const sectionNames = Array.from(sections).map((item) => item.textContent)

    for (const section of sections) {
      const id = formatStringToIdName(section.textContent)
      section.id = id
    }
  }, [])

  useEffect(() => {
    if (sectionId) {
      const target = document.querySelector(sectionId)
      target.scrollIntoView()
    }
    // (hack) prevents the selected section and the site header from overlapping on page load
    const timer = setTimeout(() => {
      setOffset(getHash() ? 90 : 0)
    }, 0)

    return () => clearTimeout(timer)
  }, [sectionId])

  const markdownConfig = {
    p: { component: Paragraph, props: { margin: { bottom: 'medium' } } },
    strong: { component: Text, props: { weight: 'bold' } },
    ol: { component: StyledList, props: { as: 'ol' } },
    ul: { component: StyledList, props: { as: 'ul' } },
    li: { component: StyledLi, props: { as: 'li' } },
    ...components
  }

  // makes sure no hydration error
  if (!markdown) return null

  return (
    <Box pad={{ vertical: 'large' }} justify="center">
      <Box width={width} margin={{ top: `${offset}px` }}>
        <Markdown components={markdownConfig}>{markdown}</Markdown>
      </Box>
    </Box>
  )
}

export default MarkdownPage
