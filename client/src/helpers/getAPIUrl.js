import { urlSearchParamsFromKeys } from 'helpers/urlSearchParamsFromKeys'

export const host = process.env.API_HOST
export const version = process.env.API_VERSION
export const path =
  // TEMP: use prod API for demo-purpose only
  // (currently staging s3 has no "SCPCP000009_multiplexed.zip - in the middle of updating etc?)
  'https://api.scpca.alexslemonade.org/v1/' || `${host}/${version}/`

export const getAPIUrl = (endpoint = '', query = {}) => {
  const url = new URL(endpoint, path)
  const search = urlSearchParamsFromKeys(query)
  url.search = search

  return url.href || url
}

export default getAPIUrl
