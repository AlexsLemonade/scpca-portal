import React from 'react'
import { useNotification } from 'hooks/useNotification'
import { Box, Text } from 'grommet'
import { Icon } from 'components/Icon'

// id is required and must be unique
export const Notification = ({
  id,
  iconColor = 'white',
  iconSize = '24px',
  fontColor = 'white',
  fontSize = '24px',
  children
}) => {
  const { notification, hideNotification } = useNotification()

  // NOTE: Do we need 'info' as well? Added 'error' state (e.g., failed API call)
  const stateMap = {
    error: {
      iconName: 'WarningNoFill',
      background: 'error'
    },
    success: {
      iconName: 'Check',
      background: 'success'
    }
  }

  if (!notification?.[id]) return null

  return (
    <Box
      background={stateMap[notification[id].state].background}
      direction="row"
      pad={{ vertical: 'medium' }}
      width="full"
    >
      <Box align="center" justify="center" width="inherit">
        <Box direction="row" align="center" justify="center">
          <Icon
            color={iconColor}
            name={stateMap[notification[id].state].iconName}
            size={iconSize}
          />
          <Box margin={{ left: 'medium' }}>
            <Text color={fontColor} size={fontSize}>
              {children}
            </Text>
          </Box>
        </Box>
      </Box>
      <Box
        pad={{ vertical: 'medium', right: '24px' }}
        onClick={() => hideNotification(id)}
        align="end"
      >
        <Icon name="Cross" color={iconColor} size={iconSize} />
      </Box>
    </Box>
  )
}

export default Notification
