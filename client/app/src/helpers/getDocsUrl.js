import { config } from 'config'

/**
 *  @name getDocsUrl
 *  @param {string} path - a partial path
 *  @description returns the full ScPCA docs URL for the given path
 *  @usage getDocsUrl("example.html") // 'https://scpca.readthedocs.io/en/stable/example.html'
 */

export const getDocsUrl = (path) => {
  return `${config.links.help}${path}`
}

export default getDocsUrl
