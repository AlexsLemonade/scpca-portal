import React from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { Button } from 'components/Button'
import { DatasetFileItems } from 'components/DatasetFileItems'
import { CCDLDatasetCopyLinkButton } from 'components/CCDLDatasetCopyLinkButton'
import { useResponsive } from 'hooks/useResponsive'
import { formatBytes } from 'helpers/formatBytes'

export const CCDLDatasetDownloadOption = ({
  dataset,
  handleDownloadDataset
}) => {
  // const { saveUserPreferences } = useDownloadOptionsContext()
  const downloadLabel = 'Download Project'

  const { responsive } = useResponsive()

  return (
    <Grid
      areas={[
        { name: 'header', start: [0, 0], end: [1, 0] },
        { name: 'body', start: [0, 1], end: [1, 1] },
        { name: 'footer', start: [0, 2], end: [1, 2] }
      ]}
      columns={['1/2', '1/2']}
      fill="vertical"
      margin={{ left: '8px', right: '8px' }}
      rows={['auto', '1fr', 'auto']}
    >
      <Box gridArea="header">
        <Heading level="3" size="small" margin={{ bottom: 'small' }}>
          Download Summary
        </Heading>
        <Box
          direction="row"
          gap="xlarge"
          margin={{ top: 'medium', bottom: 'small' }}
        >
          <Text weight="bold">CCDL Project ID: {dataset.ccdl_project_id}</Text>
          <Text weight="bold">
            Size: {formatBytes(dataset.computed_file.size_in_bytes)}
          </Text>
        </Box>
      </Box>
      <Box gridArea="body" margin={{ bottom: 'small' }}>
        <Paragraph>The download consists of the following items:</Paragraph>
        <DatasetFileItems dataset={dataset} />
      </Box>
      <Box gridArea="footer" margin={{ top: 'medium' }}>
        <Grid columns={responsive('1', '1/2')} gap="large">
          <Button
            primary
            alignSelf="start"
            aria-label={downloadLabel}
            label={downloadLabel}
            onClick={() => {
              // TODO: add new saveUserPreferences for ccdl datasets
              // saveUserPreferences()
              handleDownloadDataset(dataset)
            }}
          />
          <CCDLDatasetCopyLinkButton dataset={dataset} />
        </Grid>
      </Box>
    </Grid>
  )
}

export default CCDLDatasetDownloadOption
