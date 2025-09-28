import React from 'react'
import { Box, CheckBox } from 'grommet'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'
import { useCCDLDatasetDownloadOptionsContext } from 'hooks/useCCDLDatasetDownloadOptionsContext'

export const CCDLDatasetCheckBoxExcludeMultiplexed = () => {
  const {
    excludeMultiplexed,
    setExcludeMultiplexed,
    isExcludeMultiplexedAvailable
  } = useCCDLDatasetDownloadOptionsContext()
  const handleChange = () => setExcludeMultiplexed(!excludeMultiplexed)

  return (
    <>
      <Box direction="row">
        <CheckBox
          checked={excludeMultiplexed}
          disabled={!isExcludeMultiplexedAvailable}
          label="Exclude multiplexed samples"
          onChange={handleChange}
        />
      </Box>
      {!isExcludeMultiplexedAvailable && <WarningAnnDataMultiplexed />}
    </>
  )
}

export default CCDLDatasetCheckBoxExcludeMultiplexed
