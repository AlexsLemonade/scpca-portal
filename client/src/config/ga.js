// used in AnalyticsContext
// each key is a unique function name describing the event
// the value is the function arguments to be sent to google

const getDatasetDownloadEventName = (dataset) => {
  if (dataset.ccdl_name) {
    return `${dataset.ccdl_project_id || 'Portal Wide'} - ${dataset.ccdl_name}`
  }

  return 'User Dataset'
}

export const events = {
  donate: () => ['Donate', 'Clicked', window.location.href],
  filterChange: (filter, change) => [
    'Filter',
    `${change} ${filter}`,
    window.location
  ],
  download: (project, sample) => ['Download', 'Downloaded', sample || project],
  dataset: (dataset) => [
    'Download',
    'Downloaded',
    getDatasetDownloadEventName(dataset)
  ]
}
