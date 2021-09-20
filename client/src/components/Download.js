import React from 'react'
import { Box, Text, FormField, TextInput, CheckBox } from 'grommet'
import { Button } from 'components/Button'
import { Modal } from 'components/Modal'
import { Link } from 'components/Link'
import { ScPCAPortalContext } from 'contexts/ScPCAPortalContext'
import api from 'api'
import formatBytes from 'helpers/formatBytes'
import DownloadSVG from '../images/download-folder.svg'

// label for the checkbox needs to be component to show links
const AcceptLabel = () => {
  return (
    <Text>
      I agree to the <Link label="Terms of Service" href="/#" /> and{' '}
      <Link label="Privacy Policy" href="/#" />.
    </Text>
  )
}

// label for the checkbox needs to be component to show links
const UpdatesLabel = () => {
  return (
    <Text>
      I would like to receive occasional updates from the{' '}
      <Link label="Privacy Policy" href="https://ccdatalab.org" />.
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
    validateToken
  } = React.useContext(ScPCAPortalContext)
  const [requesting, setRequesting] = React.useState(false)
  const [errors, setErrors] = React.useState([])

  React.useEffect(() => {
    const asyncTokenRequest = async () => {
      const validation = await validateToken()
      if (validation.isValid) {
        const tokenRequest = await createToken()
        if (tokenRequest.isOK) {
          setErrors([])
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
        Please read and accept our <Link label="Terms of Service" href="/#" />{' '}
        and <Link label="Privacy Policy" href="/#" /> before you download data.
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

// View when the donwload should have been initiated
export const DownloadView = ({ computedFile }) => {
  // open the file in a new tab
  const {
    project,
    sample,
    size_in_bytes: size,
    download_url: href
  } = computedFile
  const startedText = project
    ? 'Your download for the project should have started.'
    : 'Your download for the sample should have started.'
  const idText = project
    ? `Project ID: ${project.id}`
    : `Sample ID: ${sample.id}`
  return (
    <Box>
      <Box
        direction="row"
        align="center"
        gap="large"
        pad={{ bottom: 'medium' }}
        border={{
          side: 'bottom',
          color: 'border-black',
          size: 'small'
        }}
      >
        <Box>
          <Text>{startedText}</Text>
          <Box
            direction="row"
            justify="between"
            margin={{ vertical: 'medium' }}
          >
            <Text weight="bold">{idText}</Text>
            <Text weight="bold">Size: {formatBytes(size)}</Text>
          </Box>
          <Text>
            <Link label="Click here" href={href} /> if your download has not
            started yet.
          </Text>
        </Box>
        <Box pad={{ bottom: 'medium', horizontal: 'medium' }}>
          <DownloadSVG />
        </Box>
      </Box>
      <Box
        direction="row"
        align="center"
        justify="between"
        pad={{ top: 'large' }}
      >
        <Text>Learn about what you can expect in your download file.</Text>
        <Link href="/docs">
          <Button primary label="Read Docs" />
        </Link>
      </Box>
    </Box>
  )
}

// Button and Modal to show when downloading
export const Download = ({ computedFile: publicComputedFile }) => {
  const { token } = React.useContext(ScPCAPortalContext)
  const { id, project } = publicComputedFile
  const label = project ? 'Download Project' : 'Download Sample'

  const [showing, setShowing] = React.useState(false)
  const [download, setDownload] = React.useState(false)

  const handleClick = () => {
    setShowing(true)
    if (download && download.download_url) {
      window.open(download.download_url)
    }
  }

  React.useEffect(() => {
    const asyncFetch = async () => {
      const downloadRequest = await api.computedFiles.get(id, token)
      if (downloadRequest.isOk) {
        // try to open download
        window.open(downloadRequest.response.download_url)
        setDownload(downloadRequest.response)
      }
    }

    if (!download && token && showing) asyncFetch()
  }, [download, token, showing])
  return (
    <>
      <Button
        flex="grow"
        primary
        label={label}
        disabled={!publicComputedFile}
        onClick={handleClick}
      />
      <Modal showing={showing} setShowing={setShowing} title={label}>
        <Box width="medium">
          {download ? <DownloadView computedFile={download} /> : <TokenView />}
        </Box>
      </Modal>
    </>
  )
}

export default Download
