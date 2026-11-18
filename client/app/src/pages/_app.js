import React from 'react'
import * as Sentry from '@sentry/react'
import 'regenerator-runtime/runtime'
import { Box, Grommet } from 'grommet'
import { theme } from 'theme'
import { Layout } from 'components/Layout'
import { Reset } from 'styles/Reset'
import { BannerContextProvider } from 'contexts/BannerContext'
import { MyDatasetContextProvider } from 'contexts/MyDatasetContext'
import { NotificationContextProvider } from 'contexts/NotificationContext'
import { ScPCAPortalContextProvider } from 'contexts/ScPCAPortalContext'
import { ScrollRestoreContextProvider } from 'contexts/ScrollRestoreContext'
import { AnalyticsContextProvider } from 'contexts/AnalyticsContext'
import { PageMeta } from 'components/PageMeta'
import ErrorPage from './_error'

// Used by the inner error boundary, which wraps the page component inside the Layout,
// so page errors render the error page with the header and footer
const Fallback = (sentry) => <ErrorPage sentry={sentry} />

// Used by the outer error boundary for errors outside the page, where the Layout is unavailable
const LayoutFallback = (sentry) => (
  <Box height={{ min: '100vh' }} align="center" justify="center">
    <ErrorPage sentry={sentry} />
  </Box>
)

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
        <Sentry.ErrorBoundary fallback={LayoutFallback} showDialog>
          <ScPCAPortalContextProvider>
            <ScrollRestoreContextProvider>
              <AnalyticsContextProvider>
                <PageMeta />
                <NotificationContextProvider>
                  <BannerContextProvider>
                    <MyDatasetContextProvider>
                      <Layout>
                        <Sentry.ErrorBoundary fallback={Fallback} showDialog>
                          <Component {...pageProps} />
                        </Sentry.ErrorBoundary>
                      </Layout>
                    </MyDatasetContextProvider>
                  </BannerContextProvider>
                </NotificationContextProvider>
              </AnalyticsContextProvider>
            </ScrollRestoreContextProvider>
          </ScPCAPortalContextProvider>
        </Sentry.ErrorBoundary>
      </Grommet>
    </>
  )
}

export default Portal
