import fetch from 'isomorphic-unfetch'

const parseRequestResponse = async (response) => {
  try {
    return await response.json()
  } catch {
    return {}
  }
}

// browser/server safe request api with standard pre-parsed responses
export const request = async (
  url,
  {
    headers = { 'content-type': 'application/json' },
    authorization,
    ...options
  } = {}
) => {
  const config = { headers, ...options }

  // add authorization token to headers
  if (authorization) {
    config.headers['api-key'] = authorization
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

export default request
