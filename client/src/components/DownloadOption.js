import React from 'react'
import { Box, Grid, Heading, Text } from 'grommet'
import { Button } from 'components/Button'
import { CopyLinkButton } from 'components/CopyLinkButton'
import { useDownloadOptionsContext } from 'hooks/useDownloadOptionsContext'
import { formatBytes } from 'helpers/formatBytes'
import { getDownloadOptionDetails } from 'helpers/getDownloadOptionDetails'
import { WarningMergedObjects } from 'components/WarningMergedObjects'
import { WarningMultiplexedSamples } from 'components/WarningMultiplexedSamples'

export const DownloadOption = ({ computedFile, handleSelectFile }) => {
  const { type, items, resourceId, warningFlags } =
    getDownloadOptionDetails(computedFile)
  const { saveUserPreferences } = useDownloadOptionsContext()
  const downloadLabel = `Download ${type}`

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
          <Text weight="bold">
            {type} ID: {resourceId}
          </Text>
          <Text weight="bold">
            Size: {formatBytes(computedFile.size_in_bytes)}
          </Text>
        </Box>
      </Box>
      <Box gridArea="body" margin={{ bottom: 'small' }}>
        {warningFlags.merged && <WarningMergedObjects />}
        {warningFlags.multiplexed && <WarningMultiplexedSamples />}
        <Box pad="small">
          <Text margin={{ bottom: 'small' }}>
            The download consists of the following items:
          </Text>
          <ul
            style={{
              listStylePosition: 'inside',
              listStyleType: 'square'
            }}
          >
            {items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Box>
      </Box>
      <Box gridArea="footer" margin={{ top: 'medium' }}>
        <Grid
          columns={['auto', 'auto']}
          gap='large'
        >
          <Button
            primary
            alignSelf="start"
            aria-label={downloadLabel}
            label={downloadLabel}
            target="_blank"
            onClick={() => {
              saveUserPreferences()
              handleSelectFile(computedFile)
            }}
          />
          <CopyLinkButton
            computedFile={computedFile}
          />
        </Grid>
      </Box>
    </Grid>
  )
}

export default DownloadOption
