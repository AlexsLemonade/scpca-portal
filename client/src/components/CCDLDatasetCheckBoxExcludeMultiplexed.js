import React from 'react'
import { Box, CheckBox } from 'grommet'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const CCDLDatasetCheckBoxExcludeMultiplexed = ({
  excludeMultiplexed,
  setExcludeMultiplexed,
  isExcludeMultiplexedAvailable
}) => {
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
