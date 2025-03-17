import React, { createContext, useState } from 'react'

export const NotificationContext = createContext({})

export const NotificationContextProvider = ({ children }) => {
  const [notification, setNotification] = useState({})

  const showNotification = (id, state) =>
    setNotification((prev) => ({
      ...prev,
      [id]: {
        state
      }
    }))

  const hideNotification = (id) =>
    setNotification(({ [id]: _, ...rest }) => rest)

  return (
    <NotificationContext.Provider
      value={{ notification, showNotification, hideNotification }}
    >
      {children}
    </NotificationContext.Provider>
  )
}
