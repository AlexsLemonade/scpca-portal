import React, { useState, useEffect } from 'react'
import { Box, Text } from 'grommet'
import { Icon } from 'components/Icon'
import { getReadable } from 'helpers/getReadable'
import { useAnalytics } from 'hooks/useAnalytics'

export const FilterPill = ({ option, onRemove }) => {
  return (
    <Box
      direction="row"
      onClick={onRemove}
      margin={{ right: 'medium', bottom: 'medium' }}
    >
      <Box
        background="alexs-light-blue-tint-60"
        pad={{ horizontal: 'small' }}
        round={{ corner: 'left', size: '15px' }}
        height="auto"
        margin={{ right: 'xsmall' }}
      >
        {option}
      </Box>
      <Box
        pad={{ horizontal: 'small' }}
        justify="center"
        background="alexs-light-blue-tint-60"
      >
        <Icon name="Cross" size="xsmall" color="black" />
      </Box>
    </Box>
  )
}

export const ProjectSearchFilterPills = ({
  filters: defaultFilters,
  onFilterChange
}) => {
  const { trackFilterChange } = useAnalytics()
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

  useEffect(() => {
    setFilters(getSafeDefaultFilters(defaultFilters))
  }, [defaultFilters])

  const removeFilter = (filter, option) => {
    const newFilters = { ...filters }
    newFilters[filter].splice(newFilters[filter].indexOf(option), 1)
    trackFilterChange(`${filter} - ${option}`, 'Removed')
    setFilters(newFilters)
    onFilterChange(newFilters)
  }
  const appliedFilters = Object.keys(filters).filter(
    (k) => filters[k].length > 0
  )

  // nextjs casts ints and bools to strings when parsing the query object
  // we have to do this, it could be more robust but we can do that later
  const getOption = (filter, option) => {
    const notString = typeof option !== 'string'
    const isBool = ['true', 'false'].includes(option)
    if (notString || isBool) return getReadable(filter)
    return getReadable(option)
  }

  return (
    <Box direction="row" wrap>
      {appliedFilters.length > 0 && (
        <Box margin={{ right: 'medium', bottom: 'medium' }}>
          <Text>Applied Filters: </Text>
        </Box>
      )}
      {appliedFilters.map((f) =>
        filters[f].map((o) => (
          <FilterPill
            key={`${f}-${o}`}
            option={getOption(f, o)}
            onRemove={() => removeFilter(f, o)}
          />
        ))
      )}
    </Box>
  )
}

export default ProjectSearchFilterPills
