import React from 'react'
import { Grid, Box } from 'grommet'
import { DownloadOption } from 'components/DownloadOption'
import { sortArrayByKey } from 'helpers/sortArrayByKey'

export const DownloadOptions = ({
  resource,
  computedFiles,
  handleSelectFile
}) => {
  const sortedComputedFiles = sortArrayByKey(computedFiles, 'type', [
    'PROJECT_ZIP',
    'SAMPLE_ZIP',
    'PROJECT_SPATIAL_ZIP',
    'SAMPLE_SPATIAL_ZIP'
  ])

  return (
    <Grid columns={['auto', 'auto']} gap="large" pad={{ bottom: 'medium' }}>
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
              resource={resource}
              computedFile={computedFile}
              handleSelectFile={handleSelectFile}
            />
          </Box>
        )
      })}
    </Grid>
  )
}

export default DownloadOptions
