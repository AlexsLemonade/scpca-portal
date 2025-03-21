import React, { useState } from 'react'
import { Box, Paragraph } from 'grommet'
import { DownloadTokenInputs } from 'components/DownloadTokenInputs'

// View when the user has no token in local storage yet
export const DatasetDownloadToken = () => {
  // NOTE: We use ScPCAPortalContext or a new context for Dataset for managing states
  const [acceptsTerms, setAcceptsTerms] = useState(false)
  const [email, setEmail] = useState('')
  const [wantsEmails, setWantsEmails] = useState(false)

  return (
    <Box>
      <Paragraph margin={{ bottom: 'small' }}>
        Please provide your email and we’ll let you know when it’s ready for
        download.
      </Paragraph>
      <DownloadTokenInputs
        acceptsTerms={acceptsTerms}
        email={email}
        wantsEmails={wantsEmails}
        onAcceptsTermsChange={setAcceptsTerms}
        onEmailChange={setEmail}
        onWantEmailsChange={setWantsEmails}
      />
    </Box>
  )
}

export default DatasetDownloadToken
