import { useContext } from 'react'
import { AnalyticsContext } from 'contexts/AnalyticsContext'

export const useAnalytics = () => useContext(AnalyticsContext)
