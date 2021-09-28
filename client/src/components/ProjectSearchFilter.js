import React from 'react'
import { Box, Text, CheckBox } from 'grommet'
import { Loader } from 'components/Loader'
import api from 'api'

export const ProjectSearchFilter = ({
  filters: defaultFilters = {},
  filterOptions: defaultOptions,
  onFilterChange = () => {}
}) => {
  const filterNames = {
    diagnoses: 'Diagnosis',
    seq_units: 'Sequencing Unit',
    modalities: 'Other Modalities and Data',
    technologies: 'Kits'
  }

  const getSafeDefaultFilters = (unsafeFilters) => {
    const safeFilters = {}
    Object.keys(unsafeFilters).forEach((k) => {
      safeFilters[k] =
        typeof unsafeFilters[k] === 'string'
          ? [unsafeFilters[k]]
          : unsafeFilters[k]
    })
    return safeFilters
  }

  const safeDefaultFilters = getSafeDefaultFilters(defaultFilters)
  const [filters, setFilters] = React.useState(safeDefaultFilters)
  const [filterOptions, setFilterOptions] = React.useState(defaultOptions)

  React.useEffect(() => {
    setFilters(getSafeDefaultFilters(defaultFilters))
  }, [defaultFilters])

  const hasFilterOption = (filter, option) => {
    return (filters[filter] || []).includes(option)
  }

  const toggleFilterOption = (filter, option) => {
    const newFilters = { ...filters }
    if (!hasFilterOption(filter, option)) {
      newFilters[filter] = newFilters[filter] || []
      newFilters[filter].push(option)
    } else {
      newFilters[filter].splice(newFilters[filter].indexOf(option), 1)
    }
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  React.useEffect(() => {
    const asyncGetFilterOptions = async () => {
      const request = await api.options.projects.get()
      if (request.isOk) {
        setFilterOptions(request.response)
      }
    }
    if (!filterOptions) asyncGetFilterOptions()
  })

  if (!filterOptions) return <Loader />

  const filterOrder = ['diagnoses', 'seq_units', 'modalities', 'technologies']

  return (
    <Box>
      {filterOrder.map((f, i) => (
        <Box
          key={f}
          border={i === 0 ? false : { side: 'top' }}
          pad={{ vertical: 'medium' }}
        >
          <Text weight="bold">{filterNames[f]}</Text>
          <Box pad={{ top: 'medium' }}>
            {filterOptions[f].map((o) => (
              <CheckBox
                key={`${f}-${o}`}
                label={o}
                value
                checked={hasFilterOption(f, o)}
                onChange={() => toggleFilterOption(f, o)}
              />
            ))}
          </Box>
        </Box>
      ))}
    </Box>
  )
}

export default ProjectSearchFilter
