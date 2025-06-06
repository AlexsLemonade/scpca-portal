import { getReadable } from 'helpers/getReadable'
/*
@name getReadableModality
@description returns a human-readable label of a modality token
@param {string} - a modality token retuened via API
@returns {string} a human-readable modality label
*/
export const getReadableModality = (modality) =>
  modality === 'SPATIAL'
    ? `${getReadable(modality)} Data`
    : getReadable(modality)
