import React from 'react'
import { portalWideLinks, projectLinks } from 'config/ccdlDatasets'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Grid, Paragraph, Text } from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { DatasetFileItems } from 'components/DatasetFileItems'
import { WarningMultiplexedSamples } from 'components/WarningMultiplexedSamples'
import { WarningMergedObjects } from 'components/WarningMergedObjects'
import { formatBytes } from 'helpers/formatBytes'
import { getReadable } from 'helpers/getReadable'
import { useCCDLDatasetDownloadModalContext } from 'hooks/useCCDLDatasetDownloadModalContext'
import DownloadSVG from '../images/download-folder.svg'

// View when the download should have been initiated
export const CCDLDatasetDownloadStarted = () => {
  // open the file in a new tab
  const { downloadableDataset } = useCCDLDatasetDownloadModalContext()
  const { size: responsiveSize } = useResponsive()
  const links = downloadableDataset.ccdl_project_id
    ? projectLinks
    : portalWideLinks
  const { learnMore } = links[downloadableDataset.ccdl_name]

  const isProject = !!downloadableDataset.ccdl_project_id
  const isMetadata = downloadableDataset.format === 'METADATA'
  const isSpatial = downloadableDataset.ccdl_modality === 'SPATIAL'

  const readableFormat = isSpatial
    ? getReadable('SPATIAL_SPACERANGER')
    : getReadable(downloadableDataset.format)

  return (
    <>
      <Grid
        columns={['2/3', '1/3']}
        align="center"
        gap="large"
        pad={{ bottom: 'medium' }}
      >
        <Box>
          <Paragraph>Your download should have started.</Paragraph>
          <Box
            direction="row"
            gap="xlarge"
            margin={{ top: 'small', bottom: 'small' }}
          >
            {isProject && (
              <Text weight="bold">
                Project ID: {downloadableDataset.ccdl_project_id}
              </Text>
            )}
            {!isProject && !isMetadata && (
              <Text weight="bold">Dataset Format: {readableFormat}</Text>
            )}
            {!isMetadata && (
              <Text weight="bold">
                Size:{' '}
                {formatBytes(downloadableDataset?.computed_file?.size_in_bytes)}
              </Text>
            )}
          </Box>
          {downloadableDataset.includes_files_merged && (
            <WarningMergedObjects />
          )}
          {!downloadableDataset.includes_files_merged && downloadableDataset.includes_files_multiplexed && (
            <WarningMultiplexedSamples />
          )}
          <Paragraph>The download consists of the following items:</Paragraph>
          <DatasetFileItems dataset={downloadableDataset} />
          <Paragraph margin={{ bottom: 'small' }}>
            Learn more about what you can expect in your download file{' '}
            <Link label="here" href={learnMore} />.
          </Paragraph>
          <Box>
            {responsiveSize !== 'small' && (
              <Paragraph style={{ fontStyle: 'italic' }} color="black-tint-40">
                If your download has not started, please ensure that pop-ups are
                not blocked and try again using the button below:
              </Paragraph>
            )}
          </Box>
          <Box pad={{ vertical: 'medium' }}>
            <Button
              alignSelf="start"
              aria-label="Try Again"
              label="Try Again"
              href={downloadableDataset.download_url}
              target="_blank"
            />
          </Box>
        </Box>
        <Box pad="medium">
          <DownloadSVG width="100%" height="auto" />
        </Box>
      </Grid>
    </>
  )
}

export default CCDLDatasetDownloadStarted
