import React from "react"
import { useNotification } from 'hooks/useNotification'
import { Box } from 'grommet'
import { Button } from 'components/Button'
import { Notifications } from 'components/Notifications'

export default {
    title: 'Components/Notifications'
}

export const Default = () => {
  const { showNotification } = useNotification()
  const message = "We did it!"
  const label = "Notify Me"

  return (
    <>
      <Notifications />
      <Button
        aria-label={label}
        flex="grow"
        primary
        label={label}
        onClick={() => showNotification(message)}
      />
    </>
  )
}
