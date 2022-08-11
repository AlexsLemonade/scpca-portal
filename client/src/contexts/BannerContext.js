import React, { createContext, useState } from 'react'

export const BannerContext = createContext({})

export const BannerContextProvider = ({ children }) => {
  const [showing, setShowing] = useState(false)
  const [bannerHeight, setBannerHeight] = useState(0)

  const hideBanner = () => {
    setShowing(false)
    setBannerHeight(0)
  }

  const showBanner = () => {
    setShowing(true)
    setBannerHeight(56)
  }

  return (
    <BannerContext.Provider
      value={{
        showing,
        bannerHeight,
        setBannerHeight,
        hideBanner,
        showBanner
      }}
    >
      {children}
    </BannerContext.Provider>
  )
}
