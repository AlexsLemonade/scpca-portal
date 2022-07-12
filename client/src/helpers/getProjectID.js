export const getProjectID = (project) =>
  typeof project === 'string' ? project : project.project

export default getProjectID
