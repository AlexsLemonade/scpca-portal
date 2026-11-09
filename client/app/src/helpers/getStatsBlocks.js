export const getStatsBlocks = (stats) => [
  {
    name: 'Projects',
    value: stats.projects_count || 0
  },
  {
    name: 'Cancer Types',
    value: stats.cancer_types_count || 0
  },
  {
    name: 'Total Samples',
    value: stats.samples_count || 0
  },
  {
    name: 'Labs',
    value: stats.labs_count || 0
  }
]

export default getStatsBlocks
