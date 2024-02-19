import { config } from 'config'
import slugify from './slugify'
// Returns a link of the given route and section name
// a route can be grabbed by visiting the page (e.g., 'terms-of-use', refine.bio/terms-of-use)
// all the linkable sections are listed in config.markdownLinkable[route]
export default (route, section) =>
  config.markdownLinkable[route].includes(section)
    ? `/${route}#${slugify(section)}`
    : ''
