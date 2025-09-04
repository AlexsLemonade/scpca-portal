import { useContext } from 'react'
import { ScrollPositionContext } from 'contexts/ScrollPositionContext'

// Tracks and restores scroll position when navigating between pages
export const useScrollPosition = () => {
  const {
    source,
    positions,
    setPositions,
    restorePosition,
    setRestorePosition
  } = useContext(ScrollPositionContext)

  // Call when navigating away from the current page (source) to track scrollY
  const addScrollPosition = (destination) => {
    // Overwrite existing matching value
    setPositions((prev) => {
      const updatedPositions = prev.filter(
        (p) => !(p.source === source && p.destination === destination)
      )
      return [...updatedPositions, { source, destination, y: window.scrollY }]
    })
  }

  /// Call when navigating back to the source page
  const setRestoreScrollPosition = (destination) => {
    const match = positions.find(
      (p) => destination.startsWith(p.source) && source === p.destination
    )
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
    setPositions((prev) => prev.filter((p) => p.source !== source))
    setRestorePosition(null)
  }

  return {
    addScrollPosition,
    setRestoreScrollPosition,
    restoreScrollPosition
  }
}
