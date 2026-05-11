import React from 'react'
import { config } from 'config'
import { WarningText } from 'components/WarningText'

export const WarningMultiplexedSamplesRemoved = () => (
  <WarningText
    iconMargin="none"
    iconSize="24px"
    lineBreak={false}
    link={config.links.which_projects_are_merged_objects}
    linkLabel="Learn more"
    text="Multiplexed samples have been removed"
  />
)

export default WarningMultiplexedSamplesRemoved
