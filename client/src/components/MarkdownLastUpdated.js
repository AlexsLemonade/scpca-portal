import React from 'react'
import { Box, Paragraph } from 'grommet'
import { getDateISO } from 'helpers/getDateISO'

export const LastUpdated = ({ date = getDateISO(), width = 'large' }) => (
  <Box width={width} pad={{ bottom: 'large' }}>
    <Paragraph alignSelf="start">Last updated: {date}</Paragraph>
  </Box>
)

export default LastUpdated
