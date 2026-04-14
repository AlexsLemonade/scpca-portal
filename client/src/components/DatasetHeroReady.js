import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useAnalytics } from 'hooks/useAnalytics'
import { useResponsive } from 'hooks/useResponsive'
import { api } from 'api'
import { formatBytes } from 'helpers/formatBytes'
import { getDateISO } from 'helpers/getDateISO'
import { Button } from 'components/Button'
import { DatasetCopyLinkButton } from 'components/DatasetCopyLinkButton'
import { DatasetDownloadForm } from 'components/DatasetDownloadForm'
import DownloadReady from '../images/download-folder.svg'

export const DatasetHeroReady = ({ dataset }) => {
  const { responsive } = useResponsive()
  const { email, token, surveyListForm } = useScPCAPortal()
  const { trackDataset } = useAnalytics()

  const [downloadableDataset, setDownloadableDataset] = useState(null)

  // Set download link if token is available on component mount
  useEffect(() => {
    const asyncFetch = async () => {
      const downloadRequest = await api.datasets.get(dataset.id, token)
      if (downloadRequest.isOk) {
        setDownloadableDataset(downloadRequest.response)
      }
    }

    if (token) asyncFetch()
  }, [token])

  const isDownloadDisabled = !token || !dataset.computed_file

  const handleDownload = () => {
    trackDataset(downloadableDataset)
    surveyListForm.submit({ email, scpca_last_download_date: getDateISO() })
    window.location.href = downloadableDataset.download_url
  }

  return (
    <Grid
      areas={responsive(
        [['header'], ['img'], ['content']],
        [
          ['header', 'header'],
          ['content', 'img']
        ]
      )}
      columns={responsive(['auto'], ['3/5', '2/5'])}
      justifyContent="center"
    >
      <Box gridArea="header" margin={{ bottom: 'medium' }}>
        <Heading level={1} serif size="38px">
          Your dataset is ready!
        </Heading>
      </Box>
      <Box gridArea="content" pad={{ right: 'xlarge' }}>
        {token ? (
          <Box direction="column">
            <Paragraph size="21px">
              Your dataset will be available for immediate download for 7 days.
            </Paragraph>
            <Paragraph size="21px" margin={{ bottom: 'medium' }}>
              After it expires, you can come back to this page to regenerate and
              download the dataset.
            </Paragraph>
            <Text margin={{ bottom: 'small' }} weight="bold">
              Uncompressed size: {formatBytes(dataset.estimated_size_in_bytes)}
            </Text>
            <Box
              direction={responsive('column', 'row')}
              gap="24px"
              margin={{ bottom: 'small' }}
            >
              <Button
                primary
                aria-label="Download"
                label="Download"
                disabled={isDownloadDisabled}
                onClick={handleDownload}
              />
              <DatasetCopyLinkButton dataset={dataset} />
            </Box>
          </Box>
        ) : (
          <DatasetDownloadForm />
        )}
      </Box>
      <Box gridArea="img" align={responsive('center', 'start')}>
        <DownloadReady />
      </Box>
    </Grid>
  )
}

export default DatasetHeroReady
