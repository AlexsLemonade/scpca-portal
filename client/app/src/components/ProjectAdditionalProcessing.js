import React from 'react'
import { Box, Text } from 'grommet'
import { getDocsUrl } from 'helpers/getDocsUrl'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'

export const ProjectAdditionalProcessing = ({
  projectId,
  additionalProcessing,
  hasAdditionalDocumentation = false
}) => {
  // "NA" is stored for projects without additional processing
  if (!additionalProcessing || additionalProcessing === 'NA')
    return <Text italic>Not Specified</Text>

  const docsLink = `${projectId}.html`

  return (
    <Box direction="row" gap="xsmall">
      <Text>{additionalProcessing}</Text>
      {hasAdditionalDocumentation && (
        <Link href={getDocsUrl(docsLink)} newTab>
          <Icon size="small" name="Help" />
        </Link>
      )}
    </Box>
  )
}

export default ProjectAdditionalProcessing
