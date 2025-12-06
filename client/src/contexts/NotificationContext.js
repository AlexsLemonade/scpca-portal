import React, { createContext, useState } from 'react'

export const NotificationContext = createContext({})

export const NotificationContextProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([])

  const showNotification = (message, type = 'success', id = Date.now()) =>
    setNotifications((prev) => [
      ...prev,
      {
        message,
        type,
        id
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
