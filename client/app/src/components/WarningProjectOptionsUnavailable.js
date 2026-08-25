import React from 'react'
import { WarningText } from 'components/WarningText'

export const WarningProjectOptionsUnavailable = () => (
  <WarningText
    text="Unable to prepopulate download options. Please select the correct dataset options."
    iconColor="error"
    iconMargin="none"
    iconName="WarningNoFill"
  />
)

export default WarningProjectOptionsUnavailable
