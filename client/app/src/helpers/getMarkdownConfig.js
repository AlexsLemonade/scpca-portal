import { camelcase } from 'helpers/camelcase'
/*
@name getMarkdownConfig
@description returns the markdown config object for the given route
@param {string} route - a page route for a markdown page
@param {str[]} sections - an array of the text contents of all sections (obtained via HTML elements)
@param {str[]} str - an array of the section id names
NOTE:
- The route can be obtained by visiting that page (e.g., 'terms-of-use', refine.bio/terms-of-use)
- The lengths of 'labels', 'sections' and 'ids' arrays always match
*/
export const getMarkdownConfig = (route, sections, ids) => {
  const key = camelcase(route.replace('/', '').replaceAll('-', ' '))
  const sectionNames = sections.map((x) => camelcase(x))
  const paths = {}

  sectionNames.forEach((k, i) => {
    paths[k] = {
      label: sections[i],
      path: `${route}${ids[i]}`
    }
  })

  return { [key]: paths }
}

export default getMarkdownConfig
