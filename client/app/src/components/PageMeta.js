import React from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { config } from 'config'

export const PageMeta = ({
  title = '',
  description = '',
  url = '',
  image = ''
}) => {
  const { asPath } = useRouter()

  const meta = {
    title: title ? `${title} - ${config.name}` : config.name,
    description: description || config.description,
    url: url || `${config.url}${asPath}`,
    image: image || '' // waiting on default image
  }

  return (
    <Head>
      <title>{meta.title}</title>
      <meta key="description" name="description" content={meta.description} />
      <meta key="og:title" property="og:title" content={meta.title} />
      <meta key="og:type" property="og:type" content="website" />
      <meta key="og:url" property="og:url" content={meta.url} />
      <meta
        key="og:description"
        property="og:description"
        content={meta.description}
      />
      <meta key="og:image" property="og:image" content={meta.image} />
      {/* <meta key="og:image" property="og:image" content={meta.image} /> */}
      <meta key="twitter:card" property="twitter:card" content="summary" />
      <meta key="twitter:title" property="twitter:title" content={meta.title} />
      <meta
        key="twitter:site"
        property="twitter:site"
        content="@CancerDataLab"
      />
      <meta
        key="twitter:description"
        property="twitter:description"
        content={meta.description}
      />
      {/* <meta key="twitter:image" property="twitter:image" content={meta.image} /> */}
    </Head>
  )
}

export default PageMeta
