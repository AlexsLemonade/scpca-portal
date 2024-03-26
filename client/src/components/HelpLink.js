import React from 'react'
import { Icon } from 'components/Icon'
import { Anchor, Box, Text } from 'grommet'

export const HelpLink = ({ label, link }) => {
  return (
    <Box direction="row" gap="xxsmall">
      <Text>{label}</Text>
      <Anchor href={link} target="_blank" margin={{ top: '-4px' }}>
        <Icon name="Help" size="16px" />
      </Anchor>
    </Box>
  )
}
