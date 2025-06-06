import { getReadable } from 'helpers/getReadable'
/*
@name getReadableModalities
@description returns an array of human-readable labels of modality tokens
@param {string[str]} - an array of modality tokens retuened via API
@returns {string[]} an array of human-readable modality labels
*/
export const getReadableModalities = (modalities) =>
  modalities.map((m) =>
    m === 'SPATIAL' ? `${getReadable(m)} Data` : getReadable(m)
  )
