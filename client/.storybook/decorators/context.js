import React from 'react'
import { ScPCAPortalContextProvider } from 'contexts/ScPCAPortalContext'
import { NotificationContextProvider } from 'contexts/NotificationContext'

const Context = Story => <ScPCAPortalContextProvider>
  <NotificationContextProvider>
      <Story />
  </NotificationContextProvider>
</ScPCAPortalContextProvider>;

export default Context;
