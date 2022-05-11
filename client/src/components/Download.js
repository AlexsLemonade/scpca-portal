import React from 'react'
import { Anchor, Box, Grid, Text } from 'grommet'
import { Button } from 'components/Button'
import { Modal } from 'components/Modal'
import { Link } from 'components/Link'
import { TokenView } from 'components/TokenView'
import { ScPCAPortalContext } from 'contexts/ScPCAPortalContext'
import { AnalyticsContext } from 'contexts/AnalyticsContext'
import { api } from 'api'
import { formatBytes } from 'helpers/formatBytes'
import { formatDate } from 'helpers/formatDate'
import { config } from 'config'
import { useResponsive } from 'hooks/useResponsive'
import DownloadSVG from '../images/download-folder.svg'

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
    ? `Project ID: ${project.scpca_id}`
    : `Sample ID: ${sample.scpca_id}`

  const { size: responsiveSize } = useResponsive()

  return (
    <>
      <Grid
        columns={['2/3', '1/3']}
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
          <Box gap="medium">
            {responsiveSize !== 'small' && (
              <Text italic color="black-tint-40">
                If your download has not started, please ensure that pop-ups are
                not blocked to enable automatic downloads. You can download now
                by using the button below:
              </Text>
            )}
            <Button
              alignSelf="start"
              label="Download Now"
              href={href}
              target="_blank"
            />
          </Box>
        </Box>
        <Box pad={{ bottom: 'medium', horizontal: 'medium' }}>
          <DownloadSVG width="100%" height="auto" />
        </Box>
      </Grid>
      <Box
        direction="row"
        align="center"
        justify="between"
        pad={{ top: 'large' }}
      >
        <Text>
          <Link
            href={config.links.what_downloading}
            label="Read the docs here"
          />{' '}
          to learn about what you can expect in your download file.
        </Text>
      </Box>
    </>
  )
}

// Button and Modal to show when downloading
export const Download = ({ Icon, computedFile: publicComputedFile }) => {
  const { token, email, surveyListForm } = React.useContext(ScPCAPortalContext)
  const { trackDownload } = React.useContext(AnalyticsContext)
  const { id, type, project, sample } = publicComputedFile
  const label = project ? 'Download Project' : 'Download Sample'

  const [showing, setShowing] = React.useState(false)
  const [download, setDownload] = React.useState(false)

  const handleClick = () => {
    setShowing(true)
    if (download && download.download_url) {
      trackDownload(type, project, sample)
      surveyListForm.submit({ email, scpca_last_download_date: formatDate() })
      window.open(download.download_url)
    }
  }

  React.useEffect(() => {
    const asyncFetch = async () => {
      const downloadRequest = await api.computedFiles.get(id, token)
      if (downloadRequest.isOk) {
        // try to open download
        trackDownload(type, project, sample)
        surveyListForm.submit({ email, scpca_last_download_date: formatDate() })
        window.open(downloadRequest.response.download_url)
        setDownload(downloadRequest.response)
      } else {
        console.error('clear the token and go back to that view')
      }
    }

    if (!download && token && showing) asyncFetch()
  }, [download, token, showing])
  return (
    <>
      {Icon ? (
        <Anchor icon={Icon} onClick={handleClick} />
      ) : (
        <Button
          flex="grow"
          primary
          label={label}
          disabled={!publicComputedFile}
          onClick={handleClick}
        />
      )}
      <Modal showing={showing} setShowing={setShowing} title={label}>
        <Box width={{ width: 'full' }}>
          {download ? <DownloadView computedFile={download} /> : <TokenView />}
        </Box>
      </Modal>
    </>
  )
}

export default Download
