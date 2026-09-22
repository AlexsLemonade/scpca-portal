import React from 'react'
import { WarningText } from 'components/WarningText'

export const WarningProjectOptionsUnavailable = () => (
  <WarningText
    text="Project with selected options is unavailable. Please select new download options below."
    iconColor="error"
    iconMargin="none"
    iconName="WarningNoFill"
  />
)

export default WarningProjectOptionsUnavailable
