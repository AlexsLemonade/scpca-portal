import React from 'react'
import { Text } from 'grommet'
import { Link } from 'components/Link'

// label for the checkbox needs to be component to show links
export const AcceptLabel = () => {
  return (
    <Text>
      I agree to the <Link label="Terms of Service" href="/terms-of-use" /> and{' '}
      <Link label="Privacy Policy" href="/privacy-policy" />.
    </Text>
  )
}

export default AcceptLabel
