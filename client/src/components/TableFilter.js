import React from 'react'
import { useAsyncDebounce } from 'react-table'
import { Box, Text, TextInput } from 'grommet'

export const TableFilter = ({
  globalFilter,
  setGlobalFilter,
  globalFilteredRows,
  preGlobalFilteredRows
}) => {
  const [value, setValue] = React.useState(globalFilter)
  const onChange = useAsyncDebounce((newValue) => {
    setGlobalFilter(newValue || undefined)
  }, 200)

  React.useEffect(() => {
    if (globalFilter !== value) setValue(globalFilter)
  }, [globalFilter])

  return (
    <Box gap="small" align="end">
      <Box width="320px" gap="medium" direction="row" align="center">
        <Text>Filter</Text>
        <TextInput
          value={value || ''}
          onChange={({ target: { value: newValue } }) => {
            setValue(newValue)
            onChange(newValue)
          }}
          aria-label="Filter"
        />
      </Box>
      <Text size="small" italic color="black-tint-40">
        Showing: {globalFilteredRows.length} / {preGlobalFilteredRows.length}
      </Text>
    </Box>
  )
}
