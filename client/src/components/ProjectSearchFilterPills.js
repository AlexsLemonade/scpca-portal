import React from 'react'
import { Box, Text } from 'grommet'
import { Icon } from 'components/Icon'

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

  React.useEffect(() => {
    setFilters(getSafeDefaultFilters(defaultFilters))
  }, [defaultFilters])

  const removeFilter = (filter, option) => {
    const newFilters = { ...filters }
    newFilters[filter].splice(newFilters[filter].indexOf(option), 2)
    setFilters(newFilters)
    onFilterChange(newFilters)
  }
  const appliedFilters = Object.keys(filters).filter(
    (k) => filters[k].length > 0
  )
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
            option={o}
            onRemove={() => removeFilter(f, o)}
          />
        ))
      )}
    </Box>
  )
}

export default ProjectSearchFilterPills
