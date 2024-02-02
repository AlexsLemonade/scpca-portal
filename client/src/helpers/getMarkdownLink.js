import { config } from 'config'
import formatStringToIdName from './formatStringToIdName'
// Returns a link of the gien page route and section name
// all the linkable sections are listed in config.markdownLinkable[route]
export default (route, section) =>
  config.markdownLinkable[route].includes(section)
    ? `/${route}#${formatStringToIdName(section)}`
    : ''
