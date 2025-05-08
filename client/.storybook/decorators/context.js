import React from 'react'
import { ScPCAPortalContextProvider } from 'contexts/ScPCAPortalContext'
import { DatasetSamplesTableContextProvider } from 'contexts/DatasetSamplesTableContext'
import { NotificationContextProvider } from 'contexts/NotificationContext'

const Context = Story => <ScPCAPortalContextProvider>
  <NotificationContextProvider>
    <DatasetSamplesTableContextProvider>
      <Story />
    </DatasetSamplesTableContextProvider>
  </NotificationContextProvider>
</ScPCAPortalContextProvider>;

export default Context;
