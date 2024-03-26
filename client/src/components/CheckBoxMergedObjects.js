import React from 'react'
import { CheckBox } from 'grommet'
import { HelpLink } from 'components/HelpLink'
import { config } from 'config'

export const CheckBoxMergedObjects = ({ downloadable = false }) => {
  const link = downloadable
    ? config.links.when_downloading_merged_objects
    : config.links.which_projects_are_merged_objects

  return (
    <CheckBox
      disabled={!downloadable}
      label={<HelpLink label="Merge samples into 1 object" link={link} />}
    />
  )
}

export default CheckBoxMergedObjects
