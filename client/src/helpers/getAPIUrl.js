import urlSearchParamsFromKeys from 'helpers/urlSearchParamsFromKeys'

export const host = process.env.API_HOST
export const version = process.env.API_VERSION
export const path = `${host}/${version}/`

export default (endpoint = '', query = {}) => {
  const url = new URL(endpoint, path)
  const search = urlSearchParamsFromKeys(query)
  url.search = search

  return url.href || url
}
