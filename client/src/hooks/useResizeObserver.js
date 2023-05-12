// (resource) https://tsukulog.net/2021/02/04/resize-custom-hook/
import { useEffect } from 'react'

export const useResizeObserver = (ref, callback) => {
  useEffect(() => {
    if (!ref) return null
    const element = ref.current

    const resizeObserver = new ResizeObserver((entries) => {
      const [entry] = entries
      callback(element, entry)
    })

    resizeObserver.observe(element)

    return () => resizeObserver.disconnect()
  }, [callback])

  return ref
}

export default useResizeObserver
