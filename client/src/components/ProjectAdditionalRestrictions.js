import React from 'react'
import { Box, Text } from 'grommet'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'

export const ProjectAdditionalRestrictions = ({ text, isModal = false }) => {
  const textContent = isModal
    ? `Restricted to ${text[0].toLowerCase()}${text.substring(1)}`
    : text

  if (!textContent) return <Text italic>None</Text>

  return (
    <Box direction="row" gap="xsmall">
      {isModal && <Icon name="Info" />}
      <Text>{textContent}</Text>
      <Link href="/terms-of-use#access-to-and-use-of-content" newTab>
        <Icon size="small" name="Help" />
      </Link>
    </Box>
  )
}

export default ProjectAdditionalRestrictions
