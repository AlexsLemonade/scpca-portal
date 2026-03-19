import { uniqueArray } from 'helpers/uniqueArray'

export const uniqueValuesForKey = (items = [], key) =>
  uniqueArray(items.map((i) => i[key]))

export default uniqueValuesForKey
