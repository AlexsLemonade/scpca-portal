import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Grid, Paragraph, Text } from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { formatBytes } from 'helpers/formatBytes'
import { getReadable, getReadableFiles } from 'helpers/getReadable'
import DownloadSVG from '../images/download-folder.svg'

// View when the donwload should have been initiated
export const CCDLDatasetDownloadStarted = ({ dataset }) => {
  // open the file in a new tab
  const { size: responsiveSize } = useResponsive()

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
          {dataset.format === 'METADATA' ? (
            <Box margin={{ top: 'small', bottom: 'small' }}>
              <Text>
                This download contains all of the sample metadata from every
                project in ScPCA Portal.
              </Text>
            </Box>
          ) : (
            <Box margin={{ top: 'small', bottom: 'small' }}>
              <Text weight="bold">
                Data Format: {getReadable(dataset.format)}
              </Text>
            </Box>
          )}
          <Paragraph>The download consists of the following items:</Paragraph>
          <Box pad="medium">
            <ul
              style={{
                listStylePosition: 'inside',
                listStyleType: 'square'
              }}
            >
              {dataset.format !== 'METADATA' && (
                <li>{getReadableFiles(dataset.ccdl_modality)}</li>
              )}
              {dataset.includes_files_cite_seq && <li>CITE-seq data</li>}
              {dataset.includes_files_bulk && <li>Bulk RNA-Seq data</li>}
              <li>Project and Sample Metadata</li>
            </ul>
          </Box>
          {dataset.includes_files_merged && (
            <Box margin={{ top: 'small', bottom: 'small' }}>
              <Text>Samples are merged into 1 object per project</Text>
            </Box>
          )}
          <Box margin={{ top: 'small', bottom: 'small' }}>
            <Text weight="bold">
              Size: {formatBytes(dataset.size_in_bytes)}
            </Text>
          </Box>
          <Paragraph margin={{ bottom: 'small' }}>
            Learn more about what you can expect in your download file{' '}
            <Link label="here" href=" " />.
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
              href={dataset.download_url}
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
