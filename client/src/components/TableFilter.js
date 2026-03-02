import React, { useCallback, useRef } from 'react'
import { Box, Text, TextInput } from 'grommet'

const useAsyncDebounce = (fn, delay) => {
  const timeoutRef = useRef(null)
  return useCallback(
    (...args) => {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = setTimeout(async () => {
        try {
          await fn(...args)
        } catch (e) {
          console.error(e)
        }
      }, delay)
    },
    [fn, delay]
  )
}

export const TableFilter = ({
  globalFilter,
  setGlobalFilter,
  pageIndex,
  pageSize,
  totalFilteredSize
}) => {
  const [value, setValue] = React.useState(globalFilter)
  const onChange = useAsyncDebounce((newValue) => {
    setGlobalFilter(newValue || undefined)
  }, 200)

  const start = pageIndex * pageSize + 1
  const end = Math.min(start + pageSize - 1, totalFilteredSize)

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
        Showing {start}–{end} of {totalFilteredSize}
      </Text>
    </Box>
  )
}
