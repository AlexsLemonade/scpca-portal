import React, { useEffect, useState } from 'react'
import { Box, Paragraph, Text } from 'grommet'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { DownloadTokenInputs } from 'components/DownloadTokenInputs'
import { Link } from 'components/Link'

export const DatasetDownloadForm = ({ text = '' }) => {
  const {
    token,
    email,
    setEmail,
    wantsEmails,
    setWantsEmails,
    acceptsTerms,
    setAcceptsTerms,
    createToken,
    validateToken,
    emailListForm
  } = useScPCAPortal()
  const { responsive } = useResponsive()

  const [requesting, setRequesting] = useState(false)
  const [submitting, setSubmitting] = useState(false) // Disable the button while making request
  const [errors, setErrors] = useState([])

  const handleRequestToken = () => {
    setSubmitting(true)
    if (token) {
      setRequesting(false)
    } else {
      setRequesting(true)
    }
  }

  // Request a token if none exists
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
        setSubmitting(false)
      }
    }
    if (requesting) asyncTokenRequest()
  }, [requesting])

  return (
    <Box>
      <Paragraph margin={{ bottom: 'small' }}>
        {text || (
          <>
            Please read and accept our{' '}
            <Link label="Terms of Service" href="/terms-of-use" /> and{' '}
            <Link label="Privacy Policy" href="/privacy-policy" /> before you
            download data.
          </>
        )}
      </Paragraph>
      {errors.length > 0 && (
        <Box>
          {errors.map((e) => (
            <Text key={e} color="error">
              {e}
            </Text>
          ))}
        </Box>
      )}
      <DownloadTokenInputs
        acceptsTerms={acceptsTerms}
        email={email}
        wantsEmails={wantsEmails}
        onAcceptsTermsChange={setAcceptsTerms}
        onEmailChange={setEmail}
        onWantEmailsChange={setWantsEmails}
      />

      <Box
        direction={responsive('column', 'row')}
        gap="24px"
        margin={{ top: 'medium' }}
      >
        <Button
          primary
          aria-label="Submit"
          label="Submit"
          disabled={!acceptsTerms || !email || submitting}
          onClick={handleRequestToken}
        />
      </Box>
    </Box>
  )
}

export default DatasetDownloadForm
