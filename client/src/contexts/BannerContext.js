import React, { createContext, useState } from 'react'

export const BannerContext = createContext({})

export const BannerContextProvider = ({ children }) => {
  const [showing, setShowing] = useState(false)
  const [bannerHeight, setBannerHeight] = useState(56)

  const onBannerClose = () => {
    setShowing(false)
    setBannerHeight(0)
  }

  const onBannerOpen = () => {
    setShowing(true)
    setBannerHeight(56)
  }

  return (
    <BannerContext.Provider
      value={{
        showing,
        setShowing,
        bannerHeight,
        setBannerHeight,
        onBannerClose,
        onBannerOpen
      }}
    >
      {children}
    </BannerContext.Provider>
  )
}
