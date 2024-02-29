import React from 'react'
import { Box, Paragraph } from 'grommet'
import { formatDate } from 'helpers/formatDate'

export const MarkdownLastUpdatedDate = ({ env = '', width = 'large' }) => (
  <Box width={width} pad={{ bottom: 'large' }}>
    <Paragraph alignSelf="start">Last updated: {env || formatDate()}</Paragraph>
  </Box>
)

export default MarkdownLastUpdatedDate
