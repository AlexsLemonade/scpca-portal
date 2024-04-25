import React from 'react'
import { Box, CheckBox } from 'grommet'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const CheckBoxExcludeMultiplexed = () => {
  const {
    excludeMultiplexed,
    setExcludeMultiplexed,
    isExcludeMultiplexedAvailable
  } = useDownloadOptionsContext()
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

export default CheckBoxExcludeMultiplexed
