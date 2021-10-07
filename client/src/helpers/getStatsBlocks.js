export default (stats) => [
  {
    name: 'Projects',
    value: stats.projects_count
  },
  {
    name: 'Cancer Types',
    value: stats.cancer_types_count
  },
  {
    name: 'Total Samples',
    value: stats.samples_count
  },
  {
    name: 'Labs',
    value: stats.labs_count
  }
]
