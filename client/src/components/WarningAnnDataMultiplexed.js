import React from 'react'
import { config } from 'config'
import { WarningText } from 'components/WarningText'
import { getReadable } from 'helpers/getReadable'

export const WarningAnnDataMultiplexed = () => (
  <WarningText
    lineBreak={false}
    iconMargin={{ right: 'none' }}
    text={`Multiplexed samples are not available as ${getReadable(
      'ANN_DATA'
    )}.`}
    linkLabel="Learn more"
    link={config.links.which_samples_can_download_as_anndata}
  />
)
