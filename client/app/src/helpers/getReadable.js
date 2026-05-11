import { values } from 'config/translations'

export const getReadable = (key, override = {}, base = values) => {
  const translation = { ...base, ...override }
  return translation[key] || key
}

export default getReadable
