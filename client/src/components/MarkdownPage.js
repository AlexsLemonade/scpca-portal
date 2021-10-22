import React from 'react'
import { Box, Markdown } from 'grommet'

export const MarkdownPage = ({ markdown }) => {
  if (!markdown) return 'missing'
  return (
    <Box pad={{ vertical: 'large' }} justify="center">
      <Box width="large">
        <Markdown>{markdown}</Markdown>
      </Box>
    </Box>
  )
}

export default MarkdownPage
