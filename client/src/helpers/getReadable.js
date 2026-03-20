import { readableNames, readableFiles } from 'config/readableNames'

export const getReadable = (key, dict = readableNames) => dict[key] || key

export const getReadableFiles = (key) => readableFiles[key] || getReadable(key)

// Exclusively used to append 'Data' to the SPATIAL modality in the UI
export const getReadableModality = (modality) =>
  `${getReadable(modality)}${modality === 'SPATIAL' ? ' Data' : ''}`

export default getReadable
