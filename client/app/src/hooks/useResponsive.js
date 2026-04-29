import React from 'react'
import { ResponsiveContext } from 'grommet'

export const useResponsive = () => {
  const responsiveSize = React.useContext(ResponsiveContext)
  const [size, setSize] = React.useState(responsiveSize)

  React.useEffect(() => {
    setSize(responsiveSize)
  }, [responsiveSize])

  const responsive = (small, big) => {
    if (size === 'small') return small
    return big
  }

  return {
    size,
    responsive
  }
}

export default useResponsive
