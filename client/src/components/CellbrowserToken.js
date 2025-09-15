import React, { useEffect, useState } from 'react'
import { Link } from 'components/Link'
import { Button } from 'components/Button'
import { DownloadTokenInputs } from 'components/DownloadTokenInputs'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { Box, Grid, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import VisualizeSvg from '../images/visualize.svg'

export const CellbrowserToken = () => {
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

  const { responsive, size } = useResponsive()
  const [errors, setErrors] = useState([])
  const [requesting, setRequesting] = useState(false)

  useEffect(() => {
    const asyncTokenRequest = async () => {
      const validation = await validateToken()
      if (validation.isValid) {
        const tokenRequest = await createToken()
        if (tokenRequest.isOK) {
          // quietly sign them up for emails if checked
          if (wantsEmails) {
            emailListForm.submit({ email })
          }
        }
      } else {
        // invalid set errors here
        setErrors(validation.errors)
        setRequesting(false)
      }
    }
    if (!token && requesting) asyncTokenRequest()
  }, [requesting, token])

  return (
    <Grid columns={responsive('1', ['medium', 'small'])} gap="large">
      <Box>
        <Box margin={{ bottom: 'small' }}>
          <Text size={responsive('', 'xlarge')}>
            Accept our terms of use to visualize data
          </Text>
        </Box>
        <Text>
          Please read and accept our{' '}
          <Link label="Terms of Service" href="/terms-of-use" /> and{' '}
          <Link label="Privacy Policy" href="/privacy-policy" /> before
          visualizing the data.
        </Text>
        {(errors || errors.length) &&
          Object.values(errors).map((keyErrors) =>
            keyErrors.map((keyError) => (
              <Text color="error" key="keyError">
                {keyError}
              </Text>
            ))
          )}
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
            label="Agree and continue"
            disabled={!acceptsTerms || !email || requesting}
            onClick={() => setRequesting(true)}
          />
        </Box>
      </Box>
      {size === 'large' && (
        <Box>
          <VisualizeSvg
            style={{ maxWidth: '100%', height: '100%' }}
            role="img"
            title="A diagram image for How it works"
          />
        </Box>
      )}
    </Grid>
  )
}

export default CellbrowserToken
