import React, { createContext } from 'react'
import ReactGA from 'react-ga4'
import { events } from 'config/ga'
import { capitalize } from 'helpers/capitalize'

ReactGA.initialize('G-3YR7L2222E')

export const AnalyticsContext = createContext({})

export const AnalyticsContextProvider = ({ children }) => {
  const trackEvent = (
    category,
    action,
    label,
    value,
    noninteraction = false
  ) => {
    ReactGA.event({ category, action, label, value, noninteraction })
  }

  // each event defined as `name` in config/ga
  // will be available from the context as `trackName`
  const trackEvents = {}
  Object.entries(events).forEach(([name, eventFunc]) => {
    trackEvents[`track${capitalize(name)}`] = (...args) =>
      trackEvent(...eventFunc(...args))
  })

  return (
    <AnalyticsContext.Provider
      value={{
        trackEvent,
        ...trackEvents
      }}
    >
      {children}
    </AnalyticsContext.Provider>
  )
}
