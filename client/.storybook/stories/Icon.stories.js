import React from 'react'
import { Box } from 'grommet'
import { SVGs, Icon as Component } from 'components/Icon'

export default {
  title: 'Components/Icon',
  component: Component,
  args: { SVGs }
}

export const Default = (args) => (
  <Box gap="medium" direction="row">
    {Object.keys(args.SVGs).map((i) => (
      <Box key={i}>
        <Component name={i} color="brand" />
      </Box>
    ))}
  </Box>
)
