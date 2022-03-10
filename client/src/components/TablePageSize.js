import React from 'react'
import { Box, Select, Text } from 'grommet'

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
