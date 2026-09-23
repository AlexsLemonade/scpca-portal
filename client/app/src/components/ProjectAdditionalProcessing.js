import React from 'react'
import { Box, Text } from 'grommet'
import { getDocsUrl } from 'helpers/getDocsUrl'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'

export const ProjectAdditionalProcessing = ({
  projectId,
  additionalProcessingDetails
}) => {
  if (!Object.keys(additionalProcessingDetails).length)
    return <Text italic>Not Specified</Text>

  const {
    additional_processing: additionalProcessing,
    has_additional_documentation: hasLink
  } = additionalProcessingDetails

  const docsLink = `${projectId}.html`

  return (
    <Box direction="row" gap="xsmall">
      <Text>{additionalProcessing}</Text>
      {hasLink && (
        <Link href={getDocsUrl(docsLink)} newTab>
          <Icon size="small" name="Help" />
        </Link>
      )}
    </Box>
  )
}

export default ProjectAdditionalProcessing
