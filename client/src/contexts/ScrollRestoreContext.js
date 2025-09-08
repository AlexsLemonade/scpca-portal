import React, { createContext } from 'react'
import { useRouter } from 'next/router'
import { useSessionStorage } from 'hooks/useSessionStorage'

export const ScrollRestoreContext = createContext({})

export const ScrollRestoreContextProvider = ({ children }) => {
  const { asPath: currentPath } = useRouter()
  const [positions, setPositions] = useSessionStorage('scroll-positions', [])
  const [restorePosition, setRestorePosition] = useSessionStorage(
    'restore-position',
    null
  )

  return (
    <ScrollRestoreContext.Provider
      value={{
        currentPath,
        positions,
        setPositions,
        restorePosition,
        setRestorePosition
      }}
    >
      {children}
    </ScrollRestoreContext.Provider>
  )
}
