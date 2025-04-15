import React from 'react'
import { Loader } from 'components/Loader'
import { Icon } from 'components/Icon'
import { Anchor, Box, Grid, Layer, Stack, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'

export const Modal = ({
  title,
  showing,
  setShowing,
  nondismissable,
  children,
  critical = false
}) => {
  const { responsive } = useResponsive()

  const dismissModal = () => {
    if (!nondismissable) {
      setShowing(false)
    }
  }

  return (
    <span>
      {showing && (
        <Layer
          onEsc={dismissModal}
          onClickOutside={dismissModal}
          modal
          background="white"
          border={{ color: 'black-tint-95' }}
        >
          <Stack anchor="top-right">
            <Box
              flex
              overflow="auto"
              height={{ min: 'min-content', max: '100vh' }}
              width={responsive(
                { width: '100%;' },
                { width: '100%', max: '720px' }
              )}
              pad={{ vertical: 'large', horizontal: 'xlarge' }}
              gap="none"
              align="center"
              round="xsmall"
              border={
                critical
                  ? { side: 'top', color: 'error', size: 'medium' }
                  : undefined
              }
            >
              <Grid
                areas={[
                  { name: 'header', start: [0, 0], end: [1, 0] },
                  { name: 'title', start: [0, 1], end: [1, 1] },
                  { name: 'body', start: [0, 2], end: [1, 2] },
                  { name: 'footer', start: [0, 3], end: [1, 3] }
                ]}
                columns={['1', '1']}
                rows={['auto', 'auto', '1fr', 'auto']}
              >
                {title && (
                  <Box
                    border={{
                      side: 'bottom',
                      color: 'border-black',
                      size: 'small'
                    }}
                    gridArea="title"
                    width="full"
                    height={{ min: 'min-content' }}
                    pad={{ bottom: 'medium' }}
                    margin={{ bottom: '24px' }}
                  >
                    <Text size="xlarge" style={{ whiteSpace: 'nowrap' }}>
                      {title}
                    </Text>
                  </Box>
                )}
                {children}
              </Grid>
            </Box>
            {!nondismissable && (
              <Box alignSelf="end">
                <Anchor
                  icon={<Icon color="black-tint-30" name="Cross" size="16px" />}
                  onClick={dismissModal}
                  margin="medium"
                />
              </Box>
            )}
          </Stack>
        </Layer>
      )}
    </span>
  )
}

export const ModalLoader = ({
  width = '320px',
  height = '200px',
  loaderWidth = '32px'
}) => (
  <Box align="center" justify="center" width={width} height={height}>
    <Loader width={loaderWidth} />
  </Box>
)

export const ModalHeader = ({ children }) => (
  <Box gridArea="header" width="full">
    {children}
  </Box>
)
export const ModalBody = ({ children }) => (
  <Box gridArea="body" width="full" height={{ min: 'min-content' }}>
    {children}
  </Box>
)
export const ModalFooter = ({ children }) => (
  <Box gridArea="footer" width="full">
    {children}
  </Box>
)

export default Modal
