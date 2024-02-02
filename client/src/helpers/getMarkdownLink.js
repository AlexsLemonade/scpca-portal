import { config } from 'config'
import formatStringToIdName from './formatStringToIdName'
// Returns the like of the sections of the given markdown page route
// all the linkable sections are listed in config.markdownLinkable[route]
export default (route, section) =>
  config.markdownLinkable[route].includes(section)
    ? `/${route}#${formatStringToIdName(section)}`
    : ''
