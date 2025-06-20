import React, { useState, useEffect } from 'react'
import { Box, Text, CheckBox } from 'grommet'
import { Loader } from 'components/Loader'
import { api } from 'api'
import { useAnalytics } from 'hooks/useAnalytics'
import { filterOut } from 'helpers/filterOut'
import { getReadable } from 'helpers/getReadable'
import { getReadableModality } from 'helpers/getReadableModality'

export const ProjectSearchFilter = ({
  filters: defaultFilters = {},
  filterOptions: defaultOptions,
  onFilterChange = () => {}
}) => {
  const { trackFilterChange } = useAnalytics()
  const filterNames = {
    organisms: 'Organisms',
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
  // Filter out Single-cell option
  const [filterOptions, setFilterOptions] = useState({
    ...defaultOptions,
    modalities: filterOut(defaultOptions.modalities, 'SINGLE_CELL')
  })

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

  const filterOrder = [
    'organisms',
    'diagnoses',
    'seq_units',
    'modalities',
    'technologies'
  ]

  return (
    <Box overflow="auto">
      <Box pad={{ vertical: 'medium' }} border={{ side: 'bottom' }}>
        {filterOptions.models.map((f) => (
          <Box key={f} height={{ min: 'auto' }}>
            <CheckBox
              key={f}
              label={`${getReadable(f)}`}
              value
              checked={hasFilterOption(f)}
              onChange={() => toggleFilterOption(f)}
            />
          </Box>
        ))}
      </Box>
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
                label={getReadableModality(o)}
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
