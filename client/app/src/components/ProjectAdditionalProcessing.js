import React from 'react'
import { Box, Text } from 'grommet'
import { config } from 'config'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'

export const ProjectAdditionalProcessing = ({ project }) => {
  const { scpca_id: projectId, additional_processing: additionalProcessing } =
    project

  // TODO: Update the link after the Science team update
  const helpLink = `${config.links.help}/${projectId}`

  if (!additionalProcessing) return <Text italic>Not Specified</Text>
  return (
    <Box direction="row" gap="xsmall">
      <Text>{additionalProcessing}</Text>
      <Link href={helpLink} newTab>
        <Icon size="small" name="Help" />
      </Link>
    </Box>
  )
}

export default ProjectAdditionalProcessing
