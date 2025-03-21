import React from 'react'
import { CheckBox, Text, TextInput } from 'grommet'
import { FormField } from 'components/FormField'
import { Link } from 'components/Link'

// label for the checkbox needs to be component to show links
const AcceptLabel = () => {
  return (
    <Text>
      I agree to the <Link label="Terms of Service" href="/terms-of-use" /> and{' '}
      <Link label="Privacy Policy" href="/privacy-policy" />.
    </Text>
  )
}

// label for the checkbox needs to be component to show links
const UpdatesLabel = () => {
  return (
    <Text>
      I would like to receive occasional updates from the{' '}
      <Link label="Data Lab Team" href="https://ccdatalab.org" />.
    </Text>
  )
}

export const DownloadTokenInputs = ({
  acceptsTerms,
  email,
  wantsEmails,
  onAcceptsTermsChange,
  onEmailChange,
  onWantEmailsChange
}) => (
  <>
    <FormField label="Email" labelWeight="bold" fieldWidth="250px">
      <TextInput
        value={email || ''}
        placeholder="myemail@example.com"
        onChange={({ target: { value } }) => onEmailChange(value)}
      />
    </FormField>
    <CheckBox
      label={<AcceptLabel />}
      value
      checked={acceptsTerms}
      onChange={({ target: { checked } }) => onAcceptsTermsChange(checked)}
    />
    <CheckBox
      label={<UpdatesLabel />}
      value
      checked={wantsEmails}
      onChange={({ target: { checked } }) => onWantEmailsChange(checked)}
    />
  </>
)

export default DownloadTokenInputs
