import {
  readableNames,
  readableFiles,
  readableCCDLFileItems
} from 'config/readableNames'

export const getReadable = (key, dict = readableNames) => dict[key] || key

// Exclusively used for CCDL datasets
export const getReadableCCDLFileItems = (key) => {
  const value = readableCCDLFileItems[key] || readableFiles[key]
  if (!value) {
    console.error(`Key ${key} is not present in readableCCDLFileItems`)
  }
  return value
}

export const getReadableFiles = (key) => readableFiles[key] || getReadable(key)

// Exclusively used to append 'Data' to the SPATIAL moality in the UI
export const getReadableModality = (modality) =>
  `${getReadable(modality)}${modality === 'SPATIAL' ? ' Data' : ''}`

export default getReadable
