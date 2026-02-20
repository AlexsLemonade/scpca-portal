import React from 'react'
import { Box, Select, Text } from 'grommet'

// TODO: This component is no longer used in Table. Add it to Storybook later.
export const TablePageSize = ({
  pageSize,
  setPageSize,
  pageSizeOptions,
  gotoPage
}) => {
  React.useEffect(() => {
    gotoPage(0)
  }, [pageSize])
  return (
    <Box gap="medium" direction="row" align="center" pad={{ right: 'medium' }}>
      <Text>Page Size</Text>
      <Box width="60px">
        <Select
          options={pageSizeOptions}
          value={pageSize}
          onChange={({ option }) => setPageSize(option)}
        />
      </Box>
    </Box>
  )
}

export default TablePageSize
