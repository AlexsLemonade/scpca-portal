import { useState, useEffect, useRef } from 'react'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useLocalStorage } from 'hooks/useLocalStorage'

export const useCellbrowserIframe = () => {
  const { token } = useScPCAPortal()

  const [requesting, setRequesting] = useState(false)

  const iframeRef = useRef(null)
  const [status, setStatus] = useState('Loading...')
  const [isIframeLoaded, setIsIframeLoaded] = useState(false)
  const [isIframeReady, setIsIframeReady] = useState(true)
  // the token to send to the iframe
  const [clientToken, setClientToken] = useLocalStorage(
    'cellbrowser-client-token'
  )

  const [hasError, setHasError] = useState(false)

  const tokenPayload = {
    token,
    clientToken
  }

  // 1. Fetch clientToken
  useEffect(() => {
    // fetch client token
    const fetchClientToken = async () => {
      const clientTokenResponse = await fetch('/api/cellbrowser/token/', {
        method: 'POST',
        headers: {
          'Content-type': 'application/json',
          'api-key': token
        }
      })

      if (!clientTokenResponse.ok || clientTokenResponse.status !== 200) {
        // user should have a token but show recoverable state here
        setHasError(true)
        return
      }

      const response = await clientTokenResponse.json()

      setClientToken(response.clientToken)
    }

    if (token && !clientToken) {
      setStatus('Authenticating...')
      fetchClientToken()
    }
    if (!token && clientToken) {
      setClientToken(undefined)
    }
  }, [token, clientToken])

  // 2. Listen for iframe ack
  useEffect(() => {
    const handleIframeMessage = ({ origin, data }) => {
      if (origin !== window.location.origin) return

      if (data.type === 'isReady') {
        setIsIframeReady(true)
      }
    }

    setStatus('Configuring Cellbrowser...')
    window.addEventListener('message', handleIframeMessage)
    return () => window.removeEventListener('message', handleIframeMessage)
  }, [])

  // 3. Send auth information on load.
  useEffect(() => {
    if (!token || !clientToken || !isIframeLoaded) return

    setStatus('Sending Credentials...')
    iframeRef.current.contentWindow.postMessage({
      type: 'token',
      ...tokenPayload
    })
  }, [token, clientToken, isIframeLoaded])

  return {
    token,
    iframeRef,
    isIframeReady,
    status,
    requesting,
    setRequesting,
    setIsIframeLoaded,
    hasError
  }
}
