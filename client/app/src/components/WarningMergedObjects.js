import React from 'react'
import { config } from 'config'
import { WarningText } from 'components/WarningText'

export const WarningMergedObjects = () => (
  <WarningText
    iconMargin="none"
    iconSize="24px"
    lineBreak={false}
    link={config.links.what_are_merged_objects}
    linkLabel="Learn more"
    text="Samples are not integrated."
  />
)

export default WarningMergedObjects
