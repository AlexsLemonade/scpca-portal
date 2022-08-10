import React, { createContext, useState } from 'react'

export const BannerContext = createContext({})

export const BannerContextProvider = ({ startShowing = true, children }) => {
  const [showing, setShowing] = useState(startShowing)
  const [bannerHeight, setBannerHeight] = useState(56)

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
