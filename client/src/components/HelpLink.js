import React from 'react'
import { Icon } from 'components/Icon'
import { Text, Anchor, Stack, Box } from 'grommet'

export const HelpLink = ({ label, link }) => {
  return (
    <Box align="start">
      <Stack anchor="bottom-right">
        <Box width="auto">
          <Text>{label}</Text>
        </Box>
        <Box margin={{ left: '100%' }} pad="small">
          <Anchor href={link} target="_blank">
            <Icon name="Help" size="16px" />
          </Anchor>
        </Box>
      </Stack>
    </Box>
  )
}
