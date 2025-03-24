import React, { createContext, useState } from 'react'

export const NotificationContext = createContext({})

export const NotificationContextProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([])

  const showNotification = (message, id = Date.now(), type = 'success') =>
    setNotifications((prev) => [
      ...prev,
      {
        message,
        id,
        type
      }
    ])

  const hideNotification = (id) =>
    setNotifications((prev) =>
      prev.filter((notification) => notification.id !== id)
    )

  return (
    <NotificationContext.Provider
      value={{ notifications, showNotification, hideNotification }}
    >
      {children}
    </NotificationContext.Provider>
  )
}
