import React from 'react'
import { Box } from 'grommet'
import { getCCDLDatasetFileItems } from 'helpers/getCCDLDatasetFileItems'

// TODO: rename to CCDLDatasetFileItems as well as file name
export const DatasetFileItems = ({ dataset }) => {
  const items = getCCDLDatasetFileItems(dataset)

  return (
    <Box
      as="ul"
      pad={{ bottom: 'large', left: 'large' }}
      style={{ listStyle: 'disc' }}
    >
      {items.map((item) => (
        <Box key={item} as="li" style={{ display: 'list-item' }}>
          {item}
        </Box>
      ))}
    </Box>
  )
}
