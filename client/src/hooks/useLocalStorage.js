import { useState, useEffect } from 'react'

export const useLocalStorage = (key, initialValue) => {
  // State to store our value
  // Pass initial state function to useState so logic is only executed once
  const [storedValue, setStoredValue] = useState(() => {
    try {
      // Get from local storage by key
      if (typeof window === 'undefined') return initialValue

      const item = window.localStorage.getItem(key)
      // Parse stored json or if none return initialValue
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      // If error also return initialValue
      console.error(error)
      return initialValue
    }
  })

  // Listen for changes in other tabs
  useEffect(() => {
    const handleStorageChange = (event) => {
      // ignore no key
      if (event.key !== key) return
      // TODO: Evaluate consequences of not updating state after removal.
      // if (!event.newValue) return

      try {
        setStoredValue(event.newValue ? JSON.parse(event.newValue) : initialValue);
      } catch (error) {
        console.error(error);
      }
    }

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    }
  }, [key, initialValue])

  // Return a wrapped version of useState's setter function that ...
  // ... persists the new value to localStorage.
  const setValue = (value) => {
    try {
      // Allow value to be a function so we have same API as useState
      const valueToStore =
        value instanceof Function ? value(storedValue) : value
      // Save state
      setStoredValue(valueToStore)
      // Save to local storage
      if (typeof window === 'undefined') return
      if (valueToStore === undefined) {
        // this may be a problem if we delete the key
        window.localStorage.removeItem(key)
      } else {
        window.localStorage.setItem(key, JSON.stringify(valueToStore))
      }
    } catch (error) {
      // A more advanced implementation would handle the error case
      console.error(error)
    }
  }
  return [storedValue, setValue]
}
