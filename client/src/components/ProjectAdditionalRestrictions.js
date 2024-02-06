import React from 'react'
import { Box, Text } from 'grommet'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'

export const ProjectAdditionalRestrictions = ({
  text,
  isAdditionalRestrictions,
  isModal = false
}) => {
  const textContent = isModal
    ? `Restricted to ${text[0].toLowerCase()}${text.substring(1)}`
    : text

  if (!isAdditionalRestrictions) return <Text italic>None</Text>

  return (
    <Box direction="row" gap="xsmall">
      {isModal && <Icon name="Info" />}
      <Text>{textContent}</Text>
      {/* NOTE: add a link for terms of use */}
      <Link href="#temp">
        <Icon size="small" name="Help" />
      </Link>
    </Box>
  )
}

export default ProjectAdditionalRestrictions
