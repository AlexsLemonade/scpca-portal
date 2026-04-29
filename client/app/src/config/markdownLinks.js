/*
lists of all linkable sections available in the markdown pages that were generated using the getMarkdownConfig helper
in MarkdownPage component (see the comment for logging in the component)

The data structure (in camelcase):

routeName: {
    sectionName" {
       label: 'text content of HTML element',
       path: 'route#section-id
    }
}

To use this config for a link in JSX:

<link
   label={config.routeName.sectionName.label}
   href={config.routeName.sectionName.path}
>

*/

export const termsOfUse = {
  accessToAndUseOfContent: {
    label: 'Access to and Use of Content',
    path: '/terms-of-use#access-to-and-use-of-content'
  }
}
