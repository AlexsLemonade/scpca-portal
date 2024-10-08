// used in AnalyticsContext
// each key is a unique function name describing the event
// the value is the function arguments to be sent to google

export const events = {
  donate: () => ['Donate', 'Clicked', window.location.href],
  filterChange: (filter, change) => [
    'Filter',
    `${change} ${filter}`,
    window.location
  ],
  download: (project, sample) => ['Download', 'Clicked', sample || project]
}
