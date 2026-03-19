import { uniqueArray } from 'helpers/uniqueArray'

export const uniqueValuesForKey = (items = [], key = undefined) =>
  uniqueArray(items.map((i) => i[key]))

export default uniqueValuesForKey
