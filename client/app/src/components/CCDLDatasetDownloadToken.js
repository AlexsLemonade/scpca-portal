import React, { useContext, useEffect, useState } from 'react'
import { Box, Text } from 'grommet'
import { ScPCAPortalContext } from 'contexts/ScPCAPortalContext'
import { Button } from 'components/Button'
import { DownloadTokenInputs } from 'components/DownloadTokenInputs'
import { Link } from 'components/Link'

// View when the user has no token in local storage yet
export const CCDLDatasetDownloadToken = () => {
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
      <DownloadTokenInputs
        acceptsTerms={acceptsTerms}
        email={email}
        wantsEmails={wantsEmails}
        onAcceptsTermsChange={setAcceptsTerms}
        onEmailChange={setEmail}
        onWantEmailsChange={setWantsEmails}
      />
      <Box direction="row" justify="end" margin={{ top: 'medium' }}>
        <Button
          primary
          label="Agree and Continue"
          disabled={!acceptsTerms || !email || requesting}
          onClick={() => setRequesting(true)}
        />
      </Box>
    </Box>
  )
}

export default CCDLDatasetDownloadToken
