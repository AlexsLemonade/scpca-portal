// Takes a project and return the available project formats as an array
export const getProjectFormats = (project) => {
  const formats = []

  // TODO: This shoud have own property
  if (project.has_single_cell_data) {
    formats.push('SINGLE_CELL_EXPERIMENT')
  }

  if (project.includes_anndata) {
    formats.push('ANN_DATA')
  }

  return formats
}
