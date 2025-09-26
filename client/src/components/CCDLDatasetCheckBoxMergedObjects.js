import React from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { config } from 'config'
import { HelpLink } from 'components/HelpLink'
import { InfoText } from 'components/InfoText'
import { Link } from 'components/Link'

export const CCDLDatasetCheckBoxMergedObjects = ({
  includesMerged,
  setIncludesMerged,
  isMergedObjectsAvailable
}) => {
  const handleChange = () => setIncludesMerged(!includesMerged)

  return (
    <>
      <Box direction="row">
        <CheckBox
          checked={includesMerged}
          disabled={!isMergedObjectsAvailable}
          label="Merge samples into 1 object"
          onChange={handleChange}
        />
        <HelpLink link={config.links.when_downloading_merged_objects} />
      </Box>
      {!isMergedObjectsAvailable && (
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
