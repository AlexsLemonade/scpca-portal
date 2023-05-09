import React, { createContext, useState } from 'react'

export const StickyBannerContext = createContext({})

export const StickyBannerContextProvider = ({ children }) => {
  const [show, setShow] = useState(false)
  const [stickyBannerHeight, setStickyBannerHeight] = useState(0)

  const hideStickyBanner = () => {
    setShow(false)
    setStickyBannerHeight(0)
  }

  const showStickyBanner = () => {
    setShow(true)
  }

  return (
    <StickyBannerContext.Provider
      value={{
        show,
        hideStickyBanner,
        showStickyBanner,
        stickyBannerHeight,
        setStickyBannerHeight
      }}
    >
      {children}
    </StickyBannerContext.Provider>
  )
}
