import React from 'react'
import { Box, CheckBox } from 'grommet'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'
import { useCCDLDatasetDownloadModalContext } from 'hooks/useCCDLDatasetDownloadModalContext'

export const CCDLDatasetCheckBoxExcludeMultiplexed = () => {
  const {
    excludeMultiplexed,
    setExcludeMultiplexed,
    isMultiplexedAvailable,
    format
  } = useCCDLDatasetDownloadModalContext()
  const handleChange = () => setExcludeMultiplexed(!excludeMultiplexed)
  const isDisabled =
    !isMultiplexedAvailable || format !== 'SINGLE_CELL_EXPERIMENT'

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
