import React from 'react'
import { useRouter } from 'next/router'

const ErrorPage = () => {
  const router = useRouter()

  React.useEffect(() => {
    const forceRefresh = (url) => {
      window.location = url
    }

    router.events.on('routeChangeStart', forceRefresh)
  })

  return 'An error has occurred'
}

export default ErrorPage
