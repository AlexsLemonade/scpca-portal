import React from 'react'
import { Box, CheckBox, Paragraph, TextInput } from 'grommet'
import { FormField } from 'components/FormField'
import { AcceptLabel } from 'components/AcceptLabel'
import { UpdatesLabel } from 'components/UpdatesLabel'

// View when the user has no token in local storage yet
export const DatasetDownloadToken = () => {
  return (
    <Box>
      <Paragraph margin={{ bottom: 'small' }}>
        Please provide your email and we’ll let you know when it’s ready for
        download.
      </Paragraph>
      <FormField label="Email" labelWeight="bold" fieldWidth="250px">
        <TextInput
          value=""
          placeholder="myemail@emailservice.com"
          onChange={() => {}}
        />
      </FormField>
      <CheckBox label={<AcceptLabel />} value onChange={() => {}} />
      <CheckBox label={<UpdatesLabel />} value onChange={() => {}} />
    </Box>
  )
}

export default DatasetDownloadToken
