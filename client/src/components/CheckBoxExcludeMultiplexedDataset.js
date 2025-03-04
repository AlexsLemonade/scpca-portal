import React from 'react'
import { Box, CheckBox } from 'grommet'
import { useDatasetOptionsContext } from 'hooks/useDatasetOptionsContext'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const CheckBoxExcludeMultiplexedDataset = () => {
  const {
    excludeMultiplexed,
    setExcludeMultiplexed,
    isExcludeMultiplexedAvailable
  } = useDatasetOptionsContext()

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

export default CheckBoxExcludeMultiplexedDataset
