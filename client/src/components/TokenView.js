import React, { useContext, useEffect, useState } from 'react'
import { Box, Text, FormField, TextInput, CheckBox } from 'grommet'
import { ScPCAPortalContext } from 'contexts/ScPCAPortalContext'
import { Button } from 'components/Button'
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

// View when the user has no token in local storage yet
export const TokenView = () => {
  // needs email validation
  const {
    email,
    setEmail,
    wantsEmails,
    setWantsEmails,
    acceptsTerms,
    setAcceptsTerms,
    createToken,
    validateToken,
    emailListForm
  } = useContext(ScPCAPortalContext)
  const [requesting, setRequesting] = useState(false)
  const [errors, setErrors] = useState([])

  useEffect(() => {
    const asyncTokenRequest = async () => {
      const validation = await validateToken()
      if (validation.isValid) {
        const tokenRequest = await createToken()
        if (tokenRequest.isOK) {
          setErrors([])
        }
        // quietly sign them up for emails if checked
        if (wantsEmails) {
          emailListForm.submit({ email })
        }
      } else {
        // invalid set errors here
        setErrors(validation.errors)
        setRequesting(false)
      }
    }
    if (requesting) asyncTokenRequest()
  }, [requesting])

  return (
    <Box>
      <Text>
        Please read and accept our{' '}
        <Link label="Terms of Service" href="/terms-of-use" /> and{' '}
        <Link label="Privacy Policy" href="/privacy-policy" /> before you
        download data.
      </Text>
      {(errors || errors.length) && <Text color="error">{errors}</Text>}
      <FormField label="Email">
        <TextInput
          value={email || ''}
          onChange={({ target: { value } }) => setEmail(value)}
        />
      </FormField>
      <CheckBox
        label={<AcceptLabel />}
        value
        checked={acceptsTerms}
        onChange={({ target: { checked } }) => setAcceptsTerms(checked)}
      />
      <CheckBox
        label={<UpdatesLabel />}
        value
        checked={wantsEmails}
        onChange={({ target: { checked } }) => setWantsEmails(checked)}
      />
      <Box direction="row" justify="end" margin={{ top: 'medium' }}>
        <Button
          primary
          label="Download"
          disabled={!acceptsTerms || !email || requesting}
          onClick={() => setRequesting(true)}
        />
      </Box>
    </Box>
  )
}

export default TokenView
