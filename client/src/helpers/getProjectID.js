/* eslint-disable no-nested-ternary */
/*
@name getProjectID
@description returns a project ID
@param {string || Object} project - a project ID as a string or an object containing a project ID
*/
export const getProjectID = (project) =>
  typeof project === 'string'
    ? project
    : typeof project === 'object'
    ? project.computed_files[0].project
    : null

export default getProjectID
