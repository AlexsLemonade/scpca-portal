import React from 'react'
import { ScPCAPortalContextProvider } from 'contexts/ScPCAPortalContext'
import { NotificationContextProvider } from 'contexts/NotificationContext'
import { MyDatasetContextProvider } from 'contexts/MyDatasetContext'
import dataset from '../data/user_dataset.json'

const Context = Story => {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem('dataset', JSON.stringify(dataset))
    window.localStorage.setItem('user-format', JSON.stringify(dataset.format))
    window.localStorage.setItem('datasets', JSON.stringify([dataset.id]))
  }

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
