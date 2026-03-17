import {
  readableNames,
  storableNames,
  readableFiles,
  readableCCDLFileItems
} from 'config/readableNames'

export const getReadable = (key) => readableNames[key] || key

export const getStorable = (key) => storableNames[key] || key

export const getReadableFiles = (key) => readableFiles[key] || getReadable(key)

export const getReadableCCDLFileItems = (key) => {
  const value = readableCCDLFileItems[key] || readableFiles[key]
  if (!value) {
    console.error(`Key ${key} is not present in readableCCDLFileItems`)
  }
  return value
}

export default getReadable
