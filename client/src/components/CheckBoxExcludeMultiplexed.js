import React from 'react'
import { Box, CheckBox } from 'grommet'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'
import { config } from 'config'
import { WarningText } from 'components/WarningText'

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
      {!isExcludeMultiplexedAvailable && (
        <WarningText
          iconMargin={{ right: 'none' }}
          text="Multiplexed samples are not available as AnnData (Python)."
          link={config.links.which_samples_can_download_as_anndata}
        />
      )}
    </>
  )
}

export default CheckBoxExcludeMultiplexed
