import React from 'react'
import { Box, Text } from 'grommet'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'

export const ProjectAdditionalProcessing = ({ additionalProcessing }) => {
  if (!additionalProcessing || !Object.keys(additionalProcessing).length)
    return <Text italic>Not Specified</Text>

  const { additional_processing: processingName, link } = additionalProcessing

  return (
    <Box direction="row" gap="xsmall">
      <Text>{processingName}</Text>
      {link && (
        <Link href={link} newTab>
          <Icon size="small" name="Help" />
        </Link>
      )}
    </Box>
  )
}

export default ProjectAdditionalProcessing
