export const getProjectID = (project) =>
  // eslint-disable-next-line no-nested-ternary
  typeof project === 'string'
    ? project
    : typeof project === 'object'
    ? project.computed_files[0].project
    : null

export default getProjectID
