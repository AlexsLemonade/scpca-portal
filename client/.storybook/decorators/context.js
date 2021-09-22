import React from 'react'
import { ScPCAPortalContextProvider } from 'contexts/ScPCAPortalContext'

export default (Story) => (
  <ScPCAPortalContextProvider>
    <Story />
  </ScPCAPortalContextProvider>
)
