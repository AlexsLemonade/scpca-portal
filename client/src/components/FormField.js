import React from 'react'
import { Box, Text } from 'grommet'

export const FormField = ({
  label,
  align = 'start',
  gap = '0',
  direction = 'column',
  fieldWidth = 'auto',
  labelWeight = 'normal',
  children
}) => {
  return (
    <Box direction={direction} align={align} margin={{ bottom: 'small' }}>
      <Box pad={{ right: 'medium' }}>
        <Text weight={labelWeight}>{label}</Text>
      </Box>
      <Box gap={gap} width={fieldWidth}>
        {children}
      </Box>
    </Box>
  )
}

export default FormField
