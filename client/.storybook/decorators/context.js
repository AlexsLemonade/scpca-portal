import React from 'react'
import { ScPCAPortalContextProvider } from 'contexts/ScPCAPortalContext'

const Context = Story => <ScPCAPortalContextProvider>
  <Story />
</ScPCAPortalContextProvider>;

export default Context;
