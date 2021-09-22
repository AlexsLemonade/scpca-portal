import Document, { Head, Main, NextScript } from 'next/document'
import React from 'react'
import { ServerStyleSheet } from 'styled-components'

export default class MyDocument extends Document {
  // set up styled components
  static getInitialProps({ renderPage }) {
    const sheet = new ServerStyleSheet()
    const page = renderPage((App) => (props) =>
      // eslint-disable-next-line react/jsx-props-no-spreading
      sheet.collectStyles(<App {...props} />)
    )
    const styleTags = sheet.getStyleElement()
    return { ...page, styleTags }
  }

  render() {
    return (
      <html lang="en-US">
        <Head>
          <link rel="icon" href="/favicon.svg" />
          <link rel="preconnect" href="https://fonts.googleapis.com" />
          <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin />
          <link
            href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:ital,wght@0,400;0,700;1,400&family=Zilla+Slab:wght@500&display=swap"
            rel="stylesheet"
          />
          {/* Google Analytics */}
          <script
            async
            src="https://www.googletagmanager.com/gtag/js?id=G-BYH3X5WS0V"
          />
          <script
            async
            // eslint-disable-next-line react/no-danger
            dangerouslySetInnerHTML={{
              __html:
                "window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);} gtag('js', new Date());gtag('config', 'G-3YR7L2222E');"
            }}
          />
          {/* Hotjar */}
          <script
            async
            //  eslint-disable-next-line react/no-danger
            dangerouslySetInnerHTML={{
              __html:
                "(function(h,o,t,j,a,r){h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};h._hjSettings={hjid:2569460,hjsv:6};a=o.getElementsByTagName('head')[0];r=o.createElement('script');r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;a.appendChild(r);})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');"
            }}
          />
          {this.props.styleTags}
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </html>
    )
  }
}
