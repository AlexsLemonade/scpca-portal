import React, { createContext } from 'react'
import { useRouter } from 'next/router'
import { useSessionStorage } from 'hooks/useSessionStorage'

export const ScrollPositionContext = createContext({})

export const ScrollPositionContextProvider = ({ children }) => {
  const { asPath: currentPath } = useRouter()
  const [positions, setPositions] = useSessionStorage('scroll-positions', [])
  const [restorePosition, setRestorePosition] = useSessionStorage(
    'restore-position',
    null
  )

  return (
    <ScrollPositionContext.Provider
      value={{
        currentPath,
        positions,
        setPositions,
        restorePosition,
        setRestorePosition
      }}
    >
      {children}
    </ScrollPositionContext.Provider>
  )
}
