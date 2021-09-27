import React from 'react'
import { Box } from 'grommet'
import { ProjectSearchFilterPills } from 'components/ProjectSearchFilterPills'

const filters = {
  one: ['a filter options', 'filter options two', 'another filter options']
}
export default {
  title: 'Components/ProjectSearchFilterPills',
  args: { filters }
}

export const Default = (args) => {
  const [demoFilters, setDemoFilters] = React.useState(args.filters)
  return (
    <Box pad="xlarge">
      <ProjectSearchFilterPills
        filters={demoFilters}
        onFilterChange={(newFilters) => {
          setDemoFilters(newFilters)
        }}
      />
    </Box>
  )
}
