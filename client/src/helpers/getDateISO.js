// default format(for hubspot): YYYY-MM-DD
/*
@name getDateISO
@description returns the current date in YYYY-MM-DD format (UTC timezone)
@param {date} date - an alternate date to return as ISO String
*/

export const getDateISO = (date = new Date()) =>
  date.toISOString().substring(0, 10)

export default getDateISO
