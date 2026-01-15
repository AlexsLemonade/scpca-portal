import React from 'react'
import { config } from 'config'
import { WarningText } from 'components/WarningText'

export const WarningMultiplexedSamples = () => (
  <WarningText
    iconMargin="none"
    iconSize="24px"
    lineBreak={false}
    link={config.links.what_downloading_multiplexed}
    linkLabel="Learn more"
    text="This contains multiplexed samples"
  />
)

export default WarningMultiplexedSamples
