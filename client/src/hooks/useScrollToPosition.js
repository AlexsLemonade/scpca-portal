import { useLocalStorage } from 'hooks/useLocalStorage'
// This hook takes the following params:
// - key: a key to store in localStorage
// - initialValue: an initial value for the scroll position
// It uses localStorage to store and restore the scroll position,
// and defaults back to initialValue after the position is restored.

export const useScrollToPosition = (
  key = 'scrollPosition',
  initialValue = 0
) => {
  const [scrollPosition, setScrollPosition] = useLocalStorage(key, initialValue)

  const saveScrollPosition = () => {
    setScrollPosition(window.scrollY)
  }

  const restoreScrollPosition = () => {
    if (scrollPosition !== null) {
      window.scrollTo(0, parseInt(scrollPosition, 10))
      setScrollPosition(initialValue)
    }
  }

  return {
    saveScrollPosition,
    restoreScrollPosition
  }
}
