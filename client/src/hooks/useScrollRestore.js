import { useContext } from 'react'
import { ScrollRestoreContext } from 'contexts/ScrollRestoreContext'

// Tracks and restores scroll position when navigating between pages
// source: a page whose scroll position is tracked for restoration when navigating between pages
// destination: a page that navigates back to the source page
export const useScrollRestore = () => {
  const {
    currentPath,
    positions,
    setPositions,
    restorePosition,
    setRestorePosition
  } = useContext(ScrollRestoreContext)

  // Call when navigating away from the current page (source) to track scrollY
  const saveOriginScrollPosition = (source, destination) => {
    // Overwrite existing matching value
    setPositions((prev) => {
      const updatedPositions = prev.filter(
        (p) => !(p.source === source && p.destination === destination)
      )
      return [...updatedPositions, { source, destination, y: window.scrollY }]
    })
  }

  // Call when navigating back to the source page
  const setRestoreFromDestination = (currentDestination) => {
    // Ensure the current page (currentDestination) matches the stored destination
    const match = positions.find((p) => p.destination === currentDestination)

    if (match) {
      setRestorePosition(match.y)
      setPositions((prev) => prev.filter((p) => p !== match))
    }
  }

  // Call when navigated back to the source page
  const restoreScrollPosition = () => {
    if (restorePosition) {
      window.scrollTo(0, parseInt(restorePosition, 10))
    }
    // Clear sessionStorage for this source
    setPositions((prev) => prev.filter((p) => p.source !== currentPath))
    setRestorePosition(null)
  }

  return {
    saveOriginScrollPosition,
    setRestoreFromDestination,
    restoreScrollPosition
  }
}
