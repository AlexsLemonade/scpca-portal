import React from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { config } from 'config'
import { HelpLink } from 'components/HelpLink'
import { InfoText } from 'components/InfoText'
import { Link } from 'components/Link'
import { useCCDLDatasetDownloadModalContext } from 'hooks/useCCDLDatasetDownloadModalContext'

export const CCDLDatasetCheckBoxMergedObjects = () => {
  const {
    includesMerged,
    setIncludesMerged,
    isMergedObjectsAvailable,
    modality
  } = useCCDLDatasetDownloadModalContext()
  const handleChange = () => setIncludesMerged(!includesMerged)
  const isDisabled = !isMergedObjectsAvailable || modality === 'SPATIAL'

  return (
    <>
      <Box direction="row">
        <CheckBox
          checked={includesMerged}
          disabled={isDisabled}
          label="Merge samples into 1 object"
          onChange={handleChange}
        />
        <HelpLink link={config.links.when_downloading_merged_objects} />
      </Box>
      {isDisabled && (
        <InfoText>
          <Text>
            Merged objects are not available for every project.{' '}
            <Link
              href={config.links.which_projects_are_merged_objects}
              label="Learn more"
            />
          </Text>
        </InfoText>
      )}
    </>
  )
}

export default CCDLDatasetCheckBoxMergedObjects
