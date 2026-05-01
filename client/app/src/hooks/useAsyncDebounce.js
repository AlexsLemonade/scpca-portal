import { useCallback, useRef } from 'react'

export const useAsyncDebounce = (fn, delay) => {
  const timeoutRef = useRef(null)
  return useCallback(
    (...args) => {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = setTimeout(async () => {
        try {
          await fn(...args)
        } catch (e) {
          console.error(e)
        }
      }, delay)
    },
    [fn, delay]
  )
}
