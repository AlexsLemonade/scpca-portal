/**
 *  @name mapRowsWithColumns
 *  @param {any[]} rows - an array of rows where each row is an array of values
 *  @param {string[]} columns - an array of column names
 *  @return returns a new array of objects where keys are the provided columns and values are from rows
 *
 */
export const mapRowsWithColumns = (rows, columns) =>
  rows.map((row) =>
    Object.fromEntries(row.map((value, i) => [columns[i], value]))
  )

export default mapRowsWithColumns
