import React from 'react'
import { Box, Text } from 'grommet'
import { Icon } from 'components/Icon'

export const InfoText = ({ label, iconSize = '16px', children }) => (
  <Box direction="row" align="center" gap="small">
    <Box pad={{ top: '2px' }}>
      <Icon
        size={iconSize}
        name="Info"
        role="presentation"
        aria-hidden="true"
        focusable="false"
      />
    </Box>
    {label && <Text>{label}</Text>}
    {children}
  </Box>
)

export default InfoText
