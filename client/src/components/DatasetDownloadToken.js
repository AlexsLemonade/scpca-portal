import React, { useState } from 'react'
import { Box, CheckBox, Paragraph, TextInput } from 'grommet'
import { FormField } from 'components/FormField'
import { AcceptLabel } from 'components/AcceptLabel'
import { UpdatesLabel } from 'components/UpdatesLabel'

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
      <FormField label="Email" labelWeight="bold" fieldWidth="250px">
        <TextInput
          value={email || ''}
          placeholder="myemail@example.com"
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
    </Box>
  )
}

export default DatasetDownloadToken
