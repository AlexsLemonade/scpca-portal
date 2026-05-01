import React from "react"
import { useNotification } from '@scpca-portal/app/hooks/useNotification'
import { Button } from '@scpca-portal/app/components/Button'
import { Notifications } from '@scpca-portal/app/components/Notifications'

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
