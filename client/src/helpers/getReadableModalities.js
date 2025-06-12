import { getReadable } from 'helpers/getReadable'
/*
@name getReadableModalities
@description returns an array of human-readable labels of modality tokens
@param {string[str]} - an array of modality tokens retuened via API
@returns {string[]} an array of human-readable modality labels
*/
export const getReadableModalities = (
  modalities,
  includeSingleCell = false
) => {
  const singleCellToken = 'SINGLE_CELL'
  // Remove Single-cell initially
  const filtered = modalities.filter((m) => m !== singleCellToken)
  // Prepend Single-cell if present and includeSingleCell
  const sorted =
    includeSingleCell && modalities.includes(singleCellToken)
      ? [singleCellToken, ...filtered]
      : filtered

  return sorted.map((m) =>
    m === 'SPATIAL' ? `${getReadable(m)} Data` : getReadable(m)
  )
}
