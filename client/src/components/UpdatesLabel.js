import React from 'react'
import { Text } from 'grommet'
import { Link } from 'components/Link'

// label for the checkbox needs to be component to show links
export const UpdatesLabel = () => {
  return (
    <Text>
      I would like to receive occasional updates from the{' '}
      <Link label="Data Lab Team" href="https://ccdatalab.org" />.
    </Text>
  )
}

export default UpdatesLabel
