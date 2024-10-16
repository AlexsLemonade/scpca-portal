import {
  metadata,
  combinedFiles,
  dynamicKeys,
  dataKeys,
  nonFormatKeys,
  metadataResourceInfo,
  modalityResourceInfo,
  omitKeys
} from 'config/downloadOptions'
import { objectContains } from 'helpers/objectContains'
import { getReadableFiles } from 'helpers/getReadable'
import { capitalize } from 'helpers/capitalize'

export const resolveKey = (key, computedFile) => {
  return dynamicKeys.includes(key) ? computedFile[key] : key
}

const formatFileItemByKey = (key, computedFile) => {
  const { format } = computedFile
  const readableKey = resolveKey(key, computedFile)
  const fileItem = getReadableFiles(readableKey)
  const formattedItem = nonFormatKeys.includes(key)
    ? fileItem
    : `${fileItem} as ${getReadableFiles(format)}`
  return capitalize(formattedItem, true).trim()
}

// takes the config and checks against the resource
// to present what will be inside of the downloadable file
export const getDownloadOptionDetails = (computedFile) => {
  const {
    metadata_only: metadataOnly,
    portal_metadata_only: portalMetadataOnly,
    modality,
    project,
    sample
  } = computedFile
  // helpers for info and resourceType
  const getInfo = () => {
    if (portalMetadataOnly) return metadataResourceInfo.ALL
    if (metadataOnly) return metadataResourceInfo.PROJECT
    return modalityResourceInfo[modalityResourceKey + suffix]
  }
  const getResourceType = () => {
    if (portalMetadataOnly) return 'All'
    return project ? 'Project' : 'Sample'
  }

  const isProject = !!project
  const isSample = !!sample
  const resourceId = project || sample
  const resourceType = getResourceType()
  const type = metadataOnly ? 'Sample Metadata' : resourceType

  // determine if there should be warnings
  const warningFlags = {
    merged: computedFile.includes_merged,
    multiplexed: computedFile.has_multiplexed_data
  }

  // Determine additional information to show.
  const modalityResourceKey = `${modality}_${type.toUpperCase()}`
  const suffix = computedFile.has_multiplexed_data ? '_MULTIPLEXED' : ''
  const info = getInfo()

  // Sort out what is in the file.
  const items = []
  const seenKeys = []

  // Determine if multiple items should be combined when listing.
  const appliedCombinations = combinedFiles.filter((conditions) => {
    return objectContains(computedFile, conditions.rules)
  })

  // Add downloadable items
  appliedCombinations.forEach((conditions) => {
    const formattedKeys = conditions.keys
      .map((key) => getReadableFiles(resolveKey(key, computedFile)))
      .join(', ')
    // Append the combined items to be presented.
    items.push(formatFileItemByKey(formattedKeys, computedFile))
    // Prevent rendering based on these keys again.
    seenKeys.push(...conditions.keys)
  })

  // Sometimes we want to skip specfic keys as line items.
  const omittedKeys = omitKeys
    .filter((conditions) => objectContains(computedFile, conditions.rules))
    .map((conditions) => conditions.key)

  // display readable version of values
  Array.from([...dynamicKeys, ...dataKeys])
    .filter(
      (key) =>
        !seenKeys.includes(key) &&
        !omittedKeys.includes(key) &&
        computedFile[key]
    )
    .forEach((key) => {
      items.push(formatFileItemByKey(key, computedFile))
    })

  items.push(metadata)

  return {
    type,
    items,
    info,
    metadataOnly,
    resourceId,
    resourceType,
    isProject,
    isSample,
    warningFlags
  }
}
