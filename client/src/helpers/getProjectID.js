/* eslint-disable no-nested-ternary */
import { getDefaultComputedFile } from './getDefaultComputedFile'
/*
@name getProjectID
@description returns a project ID
@param {string || Object} project - a project ID as a string or an object containing a project ID
*/
export const getProjectID = (project) =>
  typeof project === 'string'
    ? project
    : typeof project === 'object'
    ? getDefaultComputedFile(project).project
    : null

export default getProjectID
