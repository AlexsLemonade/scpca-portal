import React from 'react'
import * as Sentry from '@sentry/react'
import { Grommet } from 'grommet'
import theme from 'theme'
import { Layout } from 'components/Layout'
import { Reset } from 'styles/Reset'
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
    <>
      <Reset />
      <Grommet theme={theme}>
        <Sentry.ErrorBoundary fallback={Fallback} showDialog>
          <Layout>
            {/* eslint-disable-next-line react/jsx-props-no-spreading */}
            <Component {...pageProps} />
          </Layout>
        </Sentry.ErrorBoundary>
      </Grommet>
    </>
  )
}

export default Portal
