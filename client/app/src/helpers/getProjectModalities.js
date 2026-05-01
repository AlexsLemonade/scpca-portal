// Takes a project and return the available project modalities as an array
export const getProjectModalities = (project) => {
  const modalities = []

  if (project.has_single_cell_data) {
    modalities.push('SINGLE_CELL')
  }

  if (project.has_spatial_data) {
    modalities.push('SPATIAL')
  }

  return modalities
}
