import React, { useEffect, useRef, useState } from 'react'
import { Box, Paragraph, Text, Markdown } from 'grommet'
import styled from 'styled-components'
import getHash from 'helpers/getHash'
import slugify from 'helpers/slugify'
import Error from 'pages/_error'

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
  const sectionIds = []
  const [offset, setOffset] = useState(0)
  const wrapperRef = useRef()

  useEffect(() => {
    if (!wrapperRef.current) return

    const sections = wrapperRef.current.querySelectorAll(
      'ol > li > p:first-child > span:first-child'
    )

    // we can print this to generate a list of linkable section text node for the config
    // const sectionNames = Array.from(sections).map((item) => item.textContent)
    for (const section of sections) {
      const id = slugify(section.textContent)
      section.id = id
      sectionIds.push(`#${id}`)
    }
  }, [wrapperRef])

  useEffect(() => {
    // validates the hash value to prevent an error
    if (sectionId && sectionIds.includes(sectionId)) {
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

  if (!markdown) return <Error />

  return (
    <Box ref={wrapperRef} pad={{ vertical: 'large' }} justify="center">
      <Box width={width} margin={{ top: `${offset}px` }}>
        <Markdown components={markdownConfig}>{markdown}</Markdown>
      </Box>
    </Box>
  )
}

export default MarkdownPage
