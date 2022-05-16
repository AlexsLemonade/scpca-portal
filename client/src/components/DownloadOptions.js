import React from 'react'
import { Grid, Box } from 'grommet'
import { DownloadOption } from 'components/DownloadOption'
import { sortArrayByKey } from 'helpers/sortArrayByKey'

export const DownloadOptions = ({ computedFiles, handleSelectFile }) => {
  const sortedComputedFiles = sortArrayByKey(computedFiles, 'type', [
    'PROJECT_ZIP',
    'SAMPLE_ZIP',
    'PROJECT_SPATIAL_ZIP',
    'SAMPLE_SPATIAL_ZIP'
  ])

  return (
    <Grid columns={['1/2', '1/2']} gap="large" pad={{ bottom: 'medium' }}>
      {sortedComputedFiles.map((computedFile, i, arr) => {
        return (
          <Box
            key={computedFile.id}
            border={
              i !== arr.length - 1
                ? {
                    side: 'right',
                    color: 'border-black',
                    size: 'small'
                  }
                : false
            }
          >
            <DownloadOption
              computedFile={computedFile}
              computedFiles={computedFiles}
              handleSelectFile={handleSelectFile}
            />
          </Box>
        )
      })}
    </Grid>
  )
}

export default DownloadOptions
