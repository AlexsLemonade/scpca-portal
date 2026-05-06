import React from 'react'
import { Box } from 'grommet'
import { SVGs, Icon } from 'components/Icon'

export default {
  title: 'Components/Icon',
  args: { SVGs }
}

export const Default = (args) => (
  <Box gap="medium" direction="row">
    {Object.keys(args.SVGs).map((i) => (
      <Box key={i}>
        <Icon name={i} color="brand" />
      </Box>
    ))}
  </Box>
)
