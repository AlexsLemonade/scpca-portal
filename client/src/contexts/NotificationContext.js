import React, { createContext, useState } from 'react'

export const NotificationContext = createContext({})

export const NotificationContextProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([
    {
      test: {
        id: 'test',
        type: 'success',
        message: 'this is fun!'
      }
    }
  ])

  const showNotification = (id, message, type) =>
    setNotifications((prev) => [
      ...prev,
      {
        [id]: {
          id,
          message,
          type
        }
      }
    ])

  const hideNotification = (id) =>
    setNotifications((prev) => prev.filter((n) => n.id !== id))

  return (
    <NotificationContext.Provider
      value={{ notifications, showNotification, hideNotification }}
    >
      {children}
    </NotificationContext.Provider>
  )
}
