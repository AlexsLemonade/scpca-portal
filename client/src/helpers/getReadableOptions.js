import { getReadable } from 'helpers/getReadable'

/*
  This function takes an array of values and returns a mapped version
  that contains the presentation label and value in an object.
  This will generally be used for selects/dropdowns.
  Automatically removes duplicate entries
*/
export default (options = []) =>
  [...new Set(options)].map(
    (option) => ({ label: getReadable(option), value: option}
  ))
