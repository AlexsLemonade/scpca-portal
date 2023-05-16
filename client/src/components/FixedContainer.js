import React from 'react'
import { Box } from 'grommet'

export const FixedContainer = ({
  alignSelf = 'center',
  pad = 'xlarge',
  width = 'xlarge',
  children,
  ...props
}) => {
  return (
    <Box
      alignSelf={alignSelf}
      pad={pad}
      width={width}
      // eslint-disable-next-line react/jsx-props-no-spreading
      {...props}
    >
      {children}
    </Box>
  )
}

export default FixedContainer
