import React from 'react'
import { CheckBox } from 'grommet'
import { config } from 'config'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'
import { HelpLink } from 'components/HelpLink'

export const CheckBoxMergedObjects = ({ downloadable = false }) => {
  const { selectedMerged, setSelectedMerged } = useDownloadOptionsContext()
  const link = downloadable
    ? config.links.when_downloading_merged_objects
    : config.links.which_projects_are_merged_objects
  const handleChange = () => setSelectedMerged(!selectedMerged)

  return (
    <CheckBox
      checked={selectedMerged && downloadable}
      disabled={!downloadable}
      label={<HelpLink label="Merge samples into 1 object" link={link} />}
      onChange={handleChange}
    />
  )
}

export default CheckBoxMergedObjects
