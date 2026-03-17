import {
  readableNames,
  storableNames,
  readableFiles,
  readableFileItems
} from 'config/readableNames'

export const getReadable = (key) => readableNames[key] || key

export const getStorable = (key) => storableNames[key] || key

export const getReadableFiles = (key) => readableFiles[key] || getReadable(key)

export const getReadableFileItems = (key) => {
  const value = readableFileItems[key] || readableFiles[key]
  if (!value) console.error(`Key ${key} is not present in readableFileItems`)
  return value
}

export default getReadable
