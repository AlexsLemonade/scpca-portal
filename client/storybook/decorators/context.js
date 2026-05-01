import React from 'react'
import { ScPCAPortalContextProvider } from '@scpca-portal/app/contexts/ScPCAPortalContext'
import { NotificationContextProvider } from '@scpca-portal/app/contexts/NotificationContext'
import { MyDatasetContextProvider } from '@scpca-portal/app/contexts/MyDatasetContext'
import { CCDLDatasetDownloadModalContextProvider } from '@scpca-portal/app/contexts/CCDLDatasetDownloadModalContext'
import dataset from '@scpca-portal/storybook/data/dataset.json'

const Context = Story => {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem('dataset', JSON.stringify(dataset))
    window.localStorage.setItem('user-format', JSON.stringify(dataset.format))
    window.localStorage.setItem('datasets', JSON.stringify([dataset.id]))
  }

  return (
    <ScPCAPortalContextProvider>
      <MyDatasetContextProvider>
        <CCDLDatasetDownloadModalContextProvider datasets={[dataset]} >
          <NotificationContextProvider>
            <Story />
          </NotificationContextProvider>
        </CCDLDatasetDownloadModalContextProvider>
      </MyDatasetContextProvider>
    </ScPCAPortalContextProvider>
  )
}

export default Context
