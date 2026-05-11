import React from 'react'
import { Box, Text } from 'grommet'

export const ErrorLabel = ({ error = 'An error occurred' }) => {
  const errors = Array.isArray(error) ? error : [error]

  return (
    <Box>
      {errors.map((e) => (
        <Text key={e} color="error" size="small">
          {e}
        </Text>
      ))}
    </Box>
  )
}
