import { downloadOptions } from 'config/downloadOptions'

// takes the config and checks against the resource
// to present what will be inside of the downloadable file
export const getDownloadOptionDetails = (resource, computedFile) => {
  const { header, data, included, metadata } =
    downloadOptions[computedFile.type]

  const items = [data]

  const link = downloadOptions[computedFile.type].link || null

  Object.entries(included).forEach(([k, v]) => {
    if (resource[k]) items.push(v)
  })

  items.push(metadata)

  return { header, items, link }
}
