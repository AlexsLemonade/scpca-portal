import React from 'react'
import { useNotification } from 'hooks/useNotification'
import { Box, Text } from 'grommet'
import { Icon } from 'components/Icon'

// id is required and must be unique
const Notification = ({ notification }) => {
  const { hideNotification } = useNotification()
  const { message, id, type } = notification

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

  return (
    <Box
      background={stateMap[type].background}
      direction="row"
      pad={{ vertical: 'small' }}
      width="full"
    >
      <Box align="center" justify="center" width="inherit">
        <Box direction="row" align="center" justify="center">
          <Icon color="white" name={stateMap[type].iconName} size="24px" />
          <Box margin={{ left: 'medium' }}>
            <Text color="white" size="21px">
              {message}
            </Text>
          </Box>
        </Box>
      </Box>
      <Box
        pad={{ vertical: 'medium', right: '24px' }}
        onClick={() => hideNotification(id)}
        align="end"
      >
        <Icon name="Cross" color="white" size="24px" />
      </Box>
    </Box>
  )
}

export const Notifications = () => {
  const { notifications } = useNotification()

  return (
    <>
      {notifications.map((notification) => {
        return (
          <Notification key={notification.id} notification={notification} />
        )
      })}
    </>
  )
}

export default Notifications
