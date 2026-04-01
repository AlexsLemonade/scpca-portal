import React from 'react'
import { ResponsiveContext } from 'grommet'

export const useResponsive = () => {
  const responsiveSize = React.useContext(ResponsiveContext)
  const [size, setSize] = React.useState(responsiveSize)

  React.useEffect(() => {
    setSize(responsiveSize)
  }, [responsiveSize])

  // TODO: Temporarily add medium at the last for backward compatibility
  const responsive = (small, big = null, medium = null) => {
    if (size === 'small') return small
    if (size === 'medium') return medium || big
    return big
  }

  return {
    size,
    responsive
  }
}

export default useResponsive
