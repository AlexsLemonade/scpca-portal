import { useContext } from 'react'
import { StickyBannerContext } from 'contexts/StickyBannerContext'

export const useStickyBanner = () => useContext(StickyBannerContext)
