import React, { useEffect, useState } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'

export const PageTitle = () => {
  const router = useRouter()
  const [path, setPath] = useState('')

  useEffect(() => {
    setPath(router.asPath)
  }, [router, path])

  let title = ''

  switch (true) {
    case /\/$/.test(path):
      title = 'ScPCA Portal'
      break
    case /\/about$/.test(path):
      title = 'About - ScPCA Portal'
      break
    case /\/projects$/.test(path):
      title = 'Browse Projects - ScPCA Portal '
      break
    case /\/projects\//.test(path):
      title = `Project ID ${path.substring(10)} - ScPCA Portal`
      break
    default:
      return 'ScPCA Portal'
  }

  return (
    <Head>
      <title>{title}</title>
    </Head>
  )
}

export default PageTitle
