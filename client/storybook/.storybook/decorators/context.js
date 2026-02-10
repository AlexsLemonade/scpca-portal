import React from 'react'
import { ScPCAPortalContextProvider } from 'contexts/ScPCAPortalContext'
import { NotificationContextProvider } from 'contexts/NotificationContext'
import { MyDatasetContextProvider } from 'contexts/MyDatasetContext'

const Context = Story => {
  return (
    <ScPCAPortalContextProvider>
      <MyDatasetContextProvider>
        <NotificationContextProvider>
          <Story />
        </NotificationContextProvider>
      </MyDatasetContextProvider>
    </ScPCAPortalContextProvider>
  )
}

export default Context
