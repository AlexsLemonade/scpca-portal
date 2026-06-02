import React from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { config } from 'config'

export const PageMeta = ({
  title = '',
  description = config.description,
  url = '',
  image = `${config.url}/scpca-social-header.png`
}) => {
  const { asPath } = useRouter()

  const metaTitle = title ? `${title} - ${config.name}` : config.name
  const metaUrl = url || `${config.url}${asPath}`

  return (
    <Head>
      <title>{metaTitle}</title>
      <meta key="description" name="description" content={description} />
      <meta key="og:title" property="og:title" content={metaTitle} />
      <meta key="og:type" property="og:type" content="website" />
      <meta key="og:url" property="og:url" content={metaUrl} />
      <meta
        key="og:description"
        property="og:description"
        content={description}
      />
      <meta key="og:image" property="og:image" content={image} />
      <meta key="twitter:card" property="twitter:card" content="summary" />
      <meta key="twitter:title" property="twitter:title" content={metaTitle} />
      <meta
        key="twitter:site"
        property="twitter:site"
        content="@CancerDataLab"
      />
      <meta
        key="twitter:description"
        property="twitter:description"
        content={description}
      />
      <meta key="twitter:image" property="twitter:image" content={image} />
    </Head>
  )
}

export default PageMeta
