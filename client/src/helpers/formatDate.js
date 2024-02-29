// default format(for hubspot): YYYY-MM-DD
/*
@name formatDate
@description returns the current date in YYYY-MM-DD format (UTC timezone)
@param {date} date - a date to be formatted
*/

export const formatDate = (date = new Date()) =>
  date.toISOString().substring(0, 10)

export default formatDate
