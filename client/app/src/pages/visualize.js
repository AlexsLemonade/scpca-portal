import React from 'react'
import dynamic from 'next/dynamic'
import { useScPCAPortal } from 'hooks/useScPCAPortal'

const CellbrowserIframe = dynamic(
  () => import('../components/CellbrowserIframe'),
  { ssr: false }
)
const CellbrowserToken = dynamic(
  () =>
    import('../components/CellbrowserToken').then((m) => m.CellbrowserToken),
  { ssr: false }
)

export const CellBrowser = () => {
  const { token } = useScPCAPortal()

  if (token) {
    return <CellbrowserIframe />
  }

  return <CellbrowserToken />
}

export default CellBrowser
