import React from 'react'
import { Box, Text } from 'grommet'
import { Icon } from 'components/Icon'

export const InfoText = ({ label, children }) => (
  <Box direction="row" align="center" gap="small">
    <Box pad={{ top: '2px' }}>
      <Icon size="16px" name="Info" />
    </Box>
    {label && <Text>{label}</Text>}
    {children}
  </Box>
)

export default InfoText
