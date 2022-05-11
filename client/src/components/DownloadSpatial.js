/* eslint-disable no-nested-ternary */
import React, { useEffect, useState } from 'react'
import { Anchor, Box, Grid, Heading, Text } from 'grommet'
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

// View for showing download options without token
export const DownloadOptions = ({ setInitialView }) => {
  // const { size: responsiveSize } = useResponsive()
  const [showTokenView, setShowTokenView] = useState(false)
  const handleClick = () => {
    setShowTokenView(true)
    setInitialView(false)
  }

  return (
    <span>
      {showTokenView ? (
        <TokenView />
      ) : (
        <Grid columns={['1/2', '1/2']} gap="large" pad={{ bottom: 'medium' }}>
          <Grid
            columns={['1/2', '1/2']}
            areas={[
              { name: 'header', start: [0, 0], end: [1, 0] },
              { name: 'body', start: [0, 1], end: [1, 1] },
              { name: 'footer', start: [0, 2], end: [1, 2] }
            ]}
            border={{
              side: 'right',
              color: 'border-black',
              size: 'small'
            }}
            pad={{ left: '16px', right: '32px' }}
            rows={['auto', '1fr', 'auto']}
          >
            <Box gridArea="header">
              <Heading level="3" size="small">
                Download Single-cell Data
              </Heading>
            </Box>
            <Box gridArea="body">
              <Text>The download consists of the following items:</Text>
              <Box pad="small">
                <ul
                  style={{
                    listStylePosition: 'inside',
                    listStyleType: 'square'
                  }}
                >
                  <li>Single-cell data</li>
                  <li>Bulk RNA-seq data</li>
                  <li>CITE-seq data</li>
                  <li>Project and Sample Metadata</li>
                </ul>
              </Box>
              <Text>Size: 900 MB</Text>
            </Box>
            <Box gridArea="footer" margin={{ top: '16px' }}>
              <Box>
                <Button
                  primary
                  alignSelf="start"
                  aria-label="Download Single-cell Data"
                  href=""
                  label="Download Single-cell Data"
                  target="_blank"
                  onClick={handleClick}
                />
              </Box>
            </Box>
          </Grid>

          <Grid
            areas={[
              { name: 'header', start: [0, 0], end: [1, 0] },
              { name: 'body', start: [0, 1], end: [1, 1] },
              { name: 'footer', start: [0, 2], end: [1, 2] }
            ]}
            columns={['1/2', '1/2']}
            pad={{ left: '16px', right: '32px' }}
            rows={['auto', '1fr', 'auto']}
          >
            <Box gridArea="header">
              <Heading level="3" size="small">
                Download Spatial Data
              </Heading>
            </Box>
            <Box gridArea="body">
              <Text>The download consists of the following items:</Text>
              <Box pad="small">
                <ul
                  style={{
                    listStylePosition: 'inside',
                    listStyleType: 'square'
                  }}
                >
                  <li>Spatial data</li>
                  <li>Project and Sample Metadata</li>
                </ul>
              </Box>
              <Text>Size: 350 MB</Text>
            </Box>
            <Box gridArea="footer" margin={{ top: '16px' }}>
              <Box>
                <Button
                  primary
                  alignSelf="start"
                  aria-label="Download Spatial Data"
                  href=""
                  label="Download Spatial Data"
                  target="_blank"
                  onClick={handleClick}
                />
              </Box>
            </Box>
          </Grid>
        </Grid>
      )}
    </span>
  )
}

// View when the donwload should have been initiated
export const DownloadView = ({ computedFile, setInitialView }) => {
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

  useEffect(() => {
    setInitialView(false)
  }, [])

  return (
    <span>
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
          <Heading level="3" size="small">
            Download Single-cell Data
          </Heading>
          <Text>{startedText}</Text>
          <Box
            direction="row"
            justify="between"
            margin={{ vertical: 'medium' }}
          >
            <Text weight="bold">{idText}</Text>
            <Text weight="bold">Size: {formatBytes(size)}</Text>
          </Box>
          <Text>The download consists of the following items:</Text>
          <Box pad="medium">
            <ul
              style={{
                listStylePosition: 'inside',
                listStyleType: 'square'
              }}
            >
              <li>Single-cell data</li>
              <li>Bulk RNA-seq data</li>
              <li>CITE-seq data</li>
              <li>Project and Sample Metadata</li>
            </ul>
          </Box>
          <Box pad={{ bottom: 'medium' }}>
            <Text>
              Learn more about what you can expect in your
              <br />
              download file
              <Link
                href={
                  project
                    ? config.links.what_downloading_project
                    : config.links.what_downloading_sample
                }
                label="here"
              />
              .
            </Text>
          </Box>
          <Box>
            {responsiveSize !== 'small' && (
              <Text italic color="black-tint-40">
                If your download has not started, please ensure that pop-ups are
                not blocked and try again using the button below:
              </Text>
            )}
          </Box>
          <Box pad={{ vertical: 'medium' }}>
            <Button
              alignSelf="start"
              aria-label="Try Again"
              label="Try Again"
              href={href}
              target="_blank"
            />
          </Box>
        </Box>
        <Box pad="medium">
          <DownloadSVG width="100%" height="auto" />
        </Box>
      </Grid>
      <Grid columns={['1/2', '1/2']} pad={{ vertical: 'medium' }}>
        <Box>
          <Heading level="3" size="small">
            Download Spatial Data
          </Heading>
          <Text>Size: {formatBytes(size)}</Text>
        </Box>
        <Box>
          <Button
            secondary
            aria-label="Download Spatial Data"
            label="Download Spatial Data"
            href=""
            target="_blank"
          />
        </Box>
      </Grid>
    </span>
  )
}

// Button and Modal to show when downloading
export const DownloadSpatial = ({ Icon, computedFile: publicComputedFile }) => {
  const { token, email, surveyListForm } = React.useContext(ScPCAPortalContext)
  const { trackDownload } = React.useContext(AnalyticsContext)
  const { id, type, project, sample } = publicComputedFile
  const label = project ? 'Download Project' : 'Download Sample'

  const [showing, setShowing] = useState(false)
  const [download, setDownload] = useState(false)
  const [initalView, setInitialView] = useState(true)

  const handleClick = () => {
    setShowing(true)
    setInitialView(true)
    if (download && download.download_url) {
      trackDownload(type, project, sample)
      surveyListForm.submit({ email, scpca_last_download_date: formatDate() })
      window.open(download.download_url)
    }
  }

  useEffect(() => {
    const asyncFetch = async () => {
      const downloadRequest = await api.computedFiles.get(id, token)
      if (downloadRequest.isOk) {
        // try to open download
        trackDownload(type, project, sample)
        surveyListForm.submit({ email, scpca_last_download_date: formatDate() })
        // window.open(downloadRequest.response.download_url)
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
          aria-label={label}
          flex="grow"
          primary
          label={label}
          disabled={!publicComputedFile}
          onClick={handleClick}
        />
      )}
      <Modal
        backBtn={initalView}
        backBtnText="View Download Options"
        showing={showing}
        setShowing={setShowing}
        setInitialView={setInitialView}
        title={label}
      >
        <Box width={{ width: 'full' }}>
          {download && !initalView ? (
            <DownloadView
              computedFile={download}
              setInitialView={setInitialView}
            />
          ) : initalView ? (
            <DownloadOptions setInitialView={setInitialView} />
          ) : (
            <TokenView />
          )}
        </Box>
      </Modal>
    </>
  )
}

export default DownloadSpatial
