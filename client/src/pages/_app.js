import React from 'react'
import * as Sentry from '@sentry/react'
import 'regenerator-runtime/runtime'
import { Grommet } from 'grommet'
import { theme } from 'theme'
import { Layout } from 'components/Layout'
import { Reset } from 'styles/Reset'
import { BannerContextProvider } from 'contexts/BannerContext'
import { MyDatasetContextProvider } from 'contexts/MyDatasetContext'
import { ScPCAPortalContextProvider } from 'contexts/ScPCAPortalContext'
import { ScrollPositionContextProvider } from 'contexts/ScrollPositionContext'
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
        <Sentry.ErrorBoundary fallback={Fallback} showDialog>
          <ScPCAPortalContextProvider>
            <ScrollPositionContextProvider>
              <AnalyticsContextProvider>
                <PageTitle />
                <BannerContextProvider>
                  <MyDatasetContextProvider>
                    <Layout>
                      {/* eslint-disable-next-line react/jsx-props-no-spreading */}
                      <Component {...pageProps} />
                    </Layout>
                  </MyDatasetContextProvider>
                </BannerContextProvider>
              </AnalyticsContextProvider>
            </ScrollPositionContextProvider>
          </ScPCAPortalContextProvider>
        </Sentry.ErrorBoundary>
      </Grommet>
    </>
  )
}

export default Portal
