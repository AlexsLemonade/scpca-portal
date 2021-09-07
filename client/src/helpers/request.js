import fetch from 'isomorphic-unfetch'

const parseRequestResponse = async (response) => {
  try {
    return await response.json()
  } catch (e) {
    return {}
  }
}

// browser/server safe request api with standard pre-parsed responses
export default async (
  url,
  { headers = {}, authorization, ...options } = {}
) => {
  const config = { headers, ...options }

  // add authorization token to headers
  if (authorization) {
    config.headers.Authorization = `Token ${authorization}`
  }

  try {
    const response = await fetch(url, config)
    return {
      isOk: response.ok,
      status: response.status,
      response: await parseRequestResponse(response)
    }
  } catch (e) {
    return {
      isOk: false,
      status: e.status,
      error: e
    }
  }
}
