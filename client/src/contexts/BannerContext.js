import React, { createContext, useState } from 'react'

export const BannerContext = createContext({})

export const BannerContextProvider = ({ children }) => {
  const [show, setShow] = useState(false)
  const [bannerHeight, setBannerHeight] = useState(0)

  const hideBanner = () => {
    setShow(false)
    setBannerHeight(0)
  }

  const showBanner = () => {
    setShow(true)
  }

  return (
    <BannerContext.Provider
      value={{
        show,
        hideBanner,
        showBanner,
        bannerHeight,
        setBannerHeight
      }}
    >
      {children}
    </BannerContext.Provider>
  )
}
