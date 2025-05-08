import React from 'react'
import { Box, Grid, Paragraph, Text } from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { formatBytes } from 'helpers/formatBytes'
import { getReadable, getReadableFiles } from 'helpers/getReadable'
import DownloadSVG from '../images/download-folder.svg'

const Li = ({ children }) => (
  <Box as="li" style={{ display: 'list-item' }}>
    {children}
  </Box>
)

// This component temporarily accepts 'dataset' but it's subject to change
// Using mock data with storybook
// Modal body to show when downloading CCDL dataset
export const DatasetDownloadStarted = ({ dataset }) => {
  const {
    format,
    modality,
    includes_merged: includeMerged,
    metadata_only: metadataOnly
  } = dataset
  const fileItems = [
    modality,
    ...['has_cite_seq_data', 'has_bulk_rna_seq'].filter((key) => dataset[key])
  ].map((key) => getReadableFiles(key))

  const startedText = metadataOnly ? (
    'This download contains all of the sample metadata from every project in ScPCA Portal.'
  ) : (
    <Text weight="bold">Data Format: {getReadable(format)}</Text>
  )

  return (
    <Grid columns={['2/3', '1/3']} align="center" gap="large">
      <Box>
        <Paragraph margin="0">Your download should have started.</Paragraph>
        <Paragraph margin={{ vertical: metadataOnly ? 'small' : '0' }}>
          {startedText}
        </Paragraph>
        <Paragraph>The download consists of the following items:</Paragraph>
        <Box
          as="ul"
          margin={{ top: '0' }}
          pad={{ left: 'large' }}
          style={{ listStyle: 'disc' }}
        >
          {metadataOnly ? (
            <Li>Sample metadata from all projects</Li>
          ) : (
            <>
              {fileItems.map((item) => (
                <Li key={item}>{item}</Li>
              ))}
              <Li>Project and Sample Metadata</Li>
            </>
          )}
        </Box>
        {includeMerged && (
          <Paragraph margin="0">
            Samples are merged into 1 object per project
          </Paragraph>
        )}
        {!metadataOnly && (
          <Paragraph>
            <Text margin={{ bottom: 'small' }} weight="bold">
              Size: {formatBytes(dataset.size_in_bytes)}
            </Text>
          </Paragraph>
        )}
        <Paragraph margin={{ bottom: 'small', top: '0' }}>
          Learn more about what you can expect in your download file{' '}
          <Link label="here" href="#demo" />.
        </Paragraph>
        <Box align="start">
          <Paragraph style={{ fontStyle: 'italic' }}>
            If your download has not started, please ensure that pop-ups are not
            blocked and try again using the button below:
          </Paragraph>
          <Button label="Try Again" aria-label="Try Again" />
        </Box>
      </Box>
      <Box pad="medium">
        <DownloadSVG width="100%" height="auto" />
      </Box>
    </Grid>
  )
}

export default DatasetDownloadStarted
