import React from 'react'

export const useWaitForAsync = (func) => {
  const mountedRef = React.useRef(true)
  const [waiting, setWaiting] = React.useState(false)

  React.useEffect(
    () => () => {
      mountedRef.current = false
    },
    []
  )

  return [
    waiting,
    async (...args) => {
      if (!func) return undefined
      let value
      setWaiting(true)
      if (func) {
        value = await Promise.resolve(func(...args))
      }
      if (mountedRef.current) setWaiting(false)
      return value
    }
  ]
}

export default useWaitForAsync
