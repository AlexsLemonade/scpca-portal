import React from 'react'
import { Grommet } from 'grommet'
import theme from 'theme'

export default (Story) => (
  <Grommet theme={theme}>
    <Story />
  </Grommet>
)
