import React, { createContext, useState } from 'react'

export const BannerContext = createContext({})

export const BannerContextProvider = ({ children }) => {
  const [banner, setBanner] = useState({})

  const openBanner = (id) =>
    setBanner((prev) => ({
      ...prev,
      [id]: {
        id,
        show: true
      }
    }))

  const hideBanner = (id) =>
    setBanner((prev) => {
      const temp = { ...prev }
      delete temp[id]

      return temp
    })

  return (
    <BannerContext.Provider
      value={{
        banner,
        hideBanner,
        openBanner
      }}
    >
      {children}
    </BannerContext.Provider>
  )
}
