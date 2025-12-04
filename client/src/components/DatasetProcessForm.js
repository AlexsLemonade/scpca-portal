import React, { useEffect, useState } from 'react'
import { Box, Paragraph, Text } from 'grommet'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useResponsive } from 'hooks/useResponsive'
import { DownloadTokenInputs } from 'components/DownloadTokenInputs'
import { Button } from 'components/Button'

export const DatasetProcessForm = ({
  buttonLabel = 'Agree and Continue',
  text = '',
  onCancel = () => {},
  onContinue = () => {}
}) => {
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

  const isToken = token && !requesting

  const handleRequestToken = () => {
    setSubmitting(true)
    if (token) {
      onContinue()
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

  // Process dataset upon successful token request
  useEffect(() => {
    if (requesting && token) {
      onContinue()
    }
  }, [token, requesting])

  return (
    <Box>
      {isToken ? (
        <Paragraph>
          We’ll send a email to <Text weight="bold">{email}</Text> once the
          dataset is ready to be downloaded.
        </Paragraph>
      ) : (
        <>
          <Paragraph margin={{ bottom: 'small' }}>
            {text ||
              'Please provide your email and we’ll let you know when it’s ready for download.'}
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
        </>
      )}

      <Box direction="row" justify="end" margin={{ top: 'medium' }} />
      <Box
        align="center"
        justify="end"
        direction={responsive('column', 'row')}
        gap="medium"
      >
        <Button aria-label="Cancel" label="Cancel" onClick={onCancel} />
        <Button
          primary
          label={buttonLabel}
          disabled={!acceptsTerms || !email || submitting}
          onClick={handleRequestToken}
          loading={submitting}
        />
      </Box>
    </Box>
  )
}

export default DatasetProcessForm
