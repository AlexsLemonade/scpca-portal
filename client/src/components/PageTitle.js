import React, { useEffect, useState } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'

export const PageTitle = ({ projectTitle }) => {
  const router = useRouter()
  const [path, setPath] = useState('')

  useEffect(() => {
    setPath(router.asPath)
  }, [router, path])

  const TITLE = 'ScPCA Portal'
  let title = TITLE

  switch (true) {
    case /\/about$/.test(path):
      title = `About - ${TITLE}`
      break
    case /\/projects$/.test(path) || /\/projects\?/.test(path):
      title = `Browse Projects - ${TITLE}`
      break
    case /\/projects\//.test(path):
      title = `${projectTitle} - ${TITLE}`
      break
    default:
      break
  }

  return (
    <Head>
      <title>{title}</title>
    </Head>
  )
}

export default PageTitle
