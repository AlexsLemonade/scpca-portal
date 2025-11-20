import React from 'react'
import { config } from 'config'
import { WarningText } from 'components/WarningText'
import { getReadable } from 'helpers/getReadable'

export const WarningAnnDataMultiplexed = ({ count }) => {
  const multiplexed = count ? ` ${count} multiplexed` : 'Multiplexed'

  return (
    <WarningText
      lineBreak={false}
      iconMargin={{ right: 'none' }}
      text={`${multiplexed} samples are not available as ${getReadable(
        'ANN_DATA'
      )}.`}
      linkLabel="Learn more"
      link={config.links.which_samples_can_download_as_anndata}
    />
  )
}
