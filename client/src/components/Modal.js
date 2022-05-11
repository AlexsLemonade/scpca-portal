import React from 'react'
import { Icon } from 'components/Icon'
import { Anchor, Box, Layer, Stack, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'

export const Modal = ({
  backBtn,
  backBtnText,
  showing,
  setShowing,
  setInitialView,
  nondismissable,
  children,
  title,
  critical = false
}) => {
  const { responsive } = useResponsive()

  const backToInitialView = () => {
    setInitialView(true)
  }

  const dismissModal = () => {
    if (!nondismissable) {
      setShowing(false)
    }
  }

  return (
    <>
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
              <Box width="full" height={{ min: 'min-content' }}>
                {!backBtn && (
                  <Text
                    color="brand"
                    role="button"
                    margin={{ bottom: 'medium' }}
                    style={{ cursor: 'pointer' }}
                    onClick={backToInitialView}
                  >
                    <Icon size="16px" name="ChevronLeft" /> {backBtnText}
                  </Text>
                )}
                {title && (
                  <Box
                    width="full"
                    border={{
                      side: 'bottom',
                      color: 'border-black',
                      size: 'small'
                    }}
                    height={{ min: 'min-content' }}
                    pad={{ bottom: 'medium' }}
                    margin={{ bottom: 'medium' }}
                  >
                    <Text size="xlarge">{title}</Text>
                  </Box>
                )}
                {children}
              </Box>
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
    </>
  )
}

export default Modal
