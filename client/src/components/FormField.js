import React from 'react'
import { Box, Text } from 'grommet'

export const FormField = ({
  label,
  align = 'start',
  gap = '0',
  direction = 'column',
  selectWidth = 'auto',
  labelWeight = 'normal',
  children
}) => {
  return (
    <Box direction={direction} align={align} margin={{ bottom: 'small' }}>
      <Box margin={{ bottom: 'small' }} pad={{ right: 'medium' }}>
        <Text weight={labelWeight}>{label}</Text>
      </Box>
      <Box gap={gap} width={{ max: selectWidth }}>
        {children}
      </Box>
    </Box>
  )
}

export default FormField
