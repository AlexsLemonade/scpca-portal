import { useEffect } from 'react'
import filterWhere from 'helpers/filterWhere'

// This hook takes the following params:
// - format: currently selected data format
// - modality: currently selected modality
// - files: an array of computed files for the currently selected project
// - getOptions: a method which returns all available format options and the currently selected format
// This hook updates the available data format options based on the given 'modality'

export const useUpdateFormatOptions = (
  format,
  modality,
  files,
  getOptions,
  setFormat,
  setFormatOptions
) => {
  useEffect(() => {
    if (!modality) return

    const modalityMatchedFiles = filterWhere(files, {
      modality
    })
    const [newFormatOptions, newFormat] = getOptions(
      'format',
      format,
      modalityMatchedFiles
    )
    setFormat(newFormat)
    setFormatOptions(newFormatOptions)
  }, [modality])
}
