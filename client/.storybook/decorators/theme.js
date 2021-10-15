import React from 'react'
import { Grommet } from 'grommet'
import theme from 'theme'

const Theme = Story => <Grommet theme={theme}>
  <Story />
</Grommet>;

export default Theme;
