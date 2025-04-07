import React from 'react'
import { Box, Stack, Text } from 'grommet'
import { Button } from 'components/Button'

export const MyDatasetButton = () => {
  const count = 53
  return (
    <Stack anchor="top-right">
      <Box width="auto">
        <Button href="/" label="My Dataset" primary />
      </Box>
      <Box background="yellow" round pad="small">
        <Text>{count}</Text>
      </Box>
    </Stack>
  )
}

export default MyDatasetButton
