import React, { useEffect, useState } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'

export const PageTitle = ({ title = '' }) => {
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

  return (
    <Head>
      <title>
        {pageTitle}
        {appName}
      </title>
    </Head>
  )
}

export default PageTitle
