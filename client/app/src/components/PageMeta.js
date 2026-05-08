import React, { useEffect, useState } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { config } from 'config'

export const PageMeta = ({ title = '', description = '' }) => {
  const router = useRouter()
  const [path, setPath] = useState('')

  useEffect(() => {
    setPath(router.asPath)
  }, [router, path])

  const appName = 'ScPCA Portal'
  let pageTitle = ''

  switch (true) {
    case title.length > 0:
      pageTitle = `${title} - `
      break
    case /\/projects/.test(path):
      pageTitle = `Browse Projects - `
      break
    case /\/about$/.test(path):
      pageTitle = `About - `
      break
    default:
      break
  }

  const ogTitle = title.length > 0 ? `${title} - ${appName}` : appName
  const ogDescription = description || config.meta.description
  const ogUrl = `${config.url}${path}`

  return (
    <Head>
      <title>{`${pageTitle}${appName}`}</title>
      <meta key="description" name="description" content={ogDescription} />
      <meta key="og:title" property="og:title" content={ogTitle} />
      <meta key="og:type" property="og:type" content="website" />
      <meta key="og:url" property="og:url" content={ogUrl} />
      <meta
        key="og:description"
        property="og:description"
        content={ogDescription}
      />
      <meta key="twitter:card" property="twitter:card" content="summary" />
      <meta key="twitter:title" property="twitter:title" content={ogTitle} />
      <meta
        key="twitter:site"
        property="twitter:site"
        content="@CancerDataLab"
      />
      <meta
        key="twitter:description"
        property="twitter:description"
        content={ogDescription}
      />
    </Head>
  )
}

export default PageMeta
