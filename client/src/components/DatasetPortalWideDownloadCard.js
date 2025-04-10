import React, { useState } from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { CopyLinkButton } from 'components/CopyLinkButton'
import { HelpLink } from 'components/HelpLink'
import { Link } from 'components/Link'
import { config } from 'config'
import { formatBytes } from 'helpers/formatBytes'
import { getReadable, getReadableFiles } from 'helpers/getReadable'

const Li = ({ children }) => (
  <Box as="li" style={{ display: 'list-item' }}>
    {children}
  </Box>
)

// NOTE: This component temporaily accepts 'dataset' but it's subject to change
// Currently mock data is used via Storybook for development
export const DatasetPortalWideDownloadCard = ({ dataset }) => {
  const { responsive } = useResponsive()

  const {
    modality,
    includes_merged: includeMerged,
    metadata_only: metadataOnly
  } = dataset

  const fileItems = [
    modality,
    ...['has_cite_seq_data', 'has_bulk_rna_seq'].filter((key) => dataset[key])
  ].map((key) => getReadableFiles(key))

  const [mergeObject, setMergeObject] = useState(false)
  const handleChangeMergedObject = () => setMergeObject(!mergeObject)

  return (
    <Box elevation="medium" pad="24px" width="full">
      <Box
        border={{ side: 'bottom' }}
        margin={{ bottom: '24px' }}
        pad={{ bottom: 'medium' }}
      >
        <Link href="#demo">
          <Text weight="bold" color="brand" size="large">
            {metadataOnly
              ? 'Sample Metadata Download'
              : getReadable(dataset.format)}{' '}
            Download
          </Text>
        </Link>
      </Box>
      <Box
        as="ul"
        margin={{ top: '0', bottom: 'large' }}
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
        <Box direction="row" margin={{ bottom: '24px' }}>
          <CheckBox
            checked={mergeObject}
            label="Merge samples into one object per project"
            onChange={handleChangeMergedObject}
          />
          <HelpLink link={config.links.when_downloading_merged_objects} />
        </Box>
      )}
      <Box
        align={responsive('start', 'center')}
        direction={responsive('column', 'row')}
        gap="large"
      >
        <Box direction="column">
          {!metadataOnly && (
            <Text margin={{ bottom: 'small' }} weight="bold">
              Size: {formatBytes(dataset.size_in_bytes)}
            </Text>
          )}
          <Box
            direction={responsive('column', 'row')}
            gap="24px"
            margin={{ bottom: 'small' }}
          >
            <Button primary aria-label="Download" label="Download" />
            {!metadataOnly && <CopyLinkButton computedFile={{}} />}
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

export default DatasetPortalWideDownloadCard
