import React from 'react'
import { Anchor, Box, Layer } from 'grommet'
import { Button } from 'components/Button'
import { Icon } from 'components/Icon'
import { Loader } from 'components/Loader'
import { useResponsive } from 'hooks/useResponsive'

export const ResponsiveSheet = ({
  label = 'Show',
  show,
  setShow,
  position = 'left',
  alignSelf = 'start',
  animate = false,
  buttonStyle,
  loading = false,
  children
}) => {
  const { size } = useResponsive()
  if (size === 'large') return children
  return (
    <>
      <Button
        alignSelf={alignSelf}
        label={label}
        onClick={() => setShow(!show)}
        plain={buttonStyle === 'plain'}
        primary={buttonStyle === 'prinary'}
        secondary={buttonStyle === 'secondary'}
      />
      {show && (
        <Layer
          full="vertical"
          responsive={false}
          position={position}
          animate={animate}
          onClickOutside={() => setShow(false)}
        >
          <Box pad="large">
            <Box
              direction="row"
              width="full"
              align="start"
              justify={loading ? 'between' : 'end'}
            >
              {loading && <Loader pad="none" width="30px" />}
              <Anchor
                alignSelf="end"
                icon={<Icon color="black-tint-30" name="Cross" size="16px" />}
                onClick={() => setShow(false)}
                margin="medium"
              />
            </Box>
            <Box flex overflow="auto">
              {children}
            </Box>
          </Box>
        </Layer>
      )}
    </>
  )
}

export default ResponsiveSheet
