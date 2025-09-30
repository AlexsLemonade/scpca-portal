import React from 'react'
import { Box, CheckBox } from 'grommet'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'
import { useCCDLDatasetDownloadContext } from 'hooks/useCCDLDatasetDownloadContext'

export const CCDLDatasetCheckBoxExcludeMultiplexed = () => {
  const {
    excludeMultiplexed,
    setExcludeMultiplexed,
    isExcludeMultiplexedAvailable,
    format
  } = useCCDLDatasetDownloadContext()
  const handleChange = () => setExcludeMultiplexed(!excludeMultiplexed)
  const isDisabled = !isExcludeMultiplexedAvailable || format === 'ANN_DATA'

  return (
    <>
      <Box direction="row">
        <CheckBox
          checked={excludeMultiplexed || isDisabled}
          disabled={isDisabled}
          label="Exclude multiplexed samples"
          onChange={handleChange}
        />
      </Box>
      {isDisabled && <WarningAnnDataMultiplexed />}
    </>
  )
}

export default CCDLDatasetCheckBoxExcludeMultiplexed
