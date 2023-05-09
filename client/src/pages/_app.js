import React from 'react'
import * as Sentry from '@sentry/react'
import { Grommet } from 'grommet'
import { theme } from 'theme'
import { Layout } from 'components/Layout'
import { Reset } from 'styles/Reset'
import { StickyBannerContextProvider } from 'contexts/StickyBannerContext'
import { ScPCAPortalContextProvider } from 'contexts/ScPCAPortalContext'
import { AnalyticsContextProvider } from 'contexts/AnalyticsContext'
import { PageTitle } from 'components/PageTitle'
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
        <ScPCAPortalContextProvider>
          <AnalyticsContextProvider>
            <PageTitle />
            <StickyBannerContextProvider>
              <Layout>
                <Sentry.ErrorBoundary fallback={Fallback} showDialog>
                  {/* eslint-disable-next-line react/jsx-props-no-spreading */}
                  <Component {...pageProps} />
                </Sentry.ErrorBoundary>
              </Layout>
            </StickyBannerContextProvider>
          </AnalyticsContextProvider>
        </ScPCAPortalContextProvider>
      </Grommet>
    </>
  )
}

export default Portal
