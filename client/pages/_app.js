import React from 'react'
import '../styles/globals.css'
import * as Sentry from '@sentry/react'
import { Grommet } from 'grommet'
import theme from '../src/theme'
import Error from './_error'

const Fallback = (sentry) => {
  return <Error sentry={sentry} />
}

const Portal = ({ Component, pageProps }) => {
  // configuring sentry
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    environment: process.env.SENTRY_ENV
  })

  return (
    <Grommet theme={theme}>
      <Sentry.ErrorBoundary fallback={Fallback} showDialog>
        <>
          {/* eslint-disable-next-line react/jsx-props-no-spreading */}
          <Component {...pageProps} />
        </>
      </Sentry.ErrorBoundary>
    </Grommet>
  )
}

export default Portal
