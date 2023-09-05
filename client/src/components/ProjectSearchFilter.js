import React, { useState, useEffect } from 'react'
import { Box, Text, CheckBox } from 'grommet'
import { Loader } from 'components/Loader'
import { api } from 'api'
import { useAnalytics } from 'hooks/useAnalytics'

export const ProjectSearchFilter = ({
  filters: defaultFilters = {},
  filterOptions: defaultOptions,
  onFilterChange = () => {}
}) => {
  const { trackFilterChange } = useAnalytics()
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
  const [filters, setFilters] = useState(safeDefaultFilters)
  const [filterOptions, setFilterOptions] = useState(defaultOptions)

  useEffect(() => {
    setFilters(getSafeDefaultFilters(defaultFilters))
  }, [defaultFilters])

  const hasFilterOption = (filter, option) => {
    if (option) {
      return (filters[filter] || []).includes(option)
    }
    return filter in filters
  }

  const toggleFilterOption = (filter, option) => {
    const newFilters = { ...filters }
    let change = 'Added'

    if (!hasFilterOption(filter, option)) {
      if (option) {
        newFilters[filter] = newFilters[filter] || []
        newFilters[filter].push(option)
      } else {
        newFilters[filter] = [true]
      }
    } else if (option) {
      change = 'Removed'
      newFilters[filter].splice(newFilters[filter].indexOf(option), 1)
    } else {
      change = 'Removed'
      delete newFilters[filter]
    }
    trackFilterChange(`${filter} - ${option}`, change)
    setFilters(newFilters)
    onFilterChange(newFilters)
  }

  useEffect(() => {
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
    <Box overflow="auto">
      {filterOrder.map((f, i) => (
        <Box
          key={f}
          border={i === 0 ? false : { side: 'top' }}
          pad={{ vertical: 'medium' }}
          height={{ min: 'auto' }}
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
