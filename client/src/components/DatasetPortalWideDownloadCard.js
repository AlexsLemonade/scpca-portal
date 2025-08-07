import React, { useState } from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { CopyLinkButton } from 'components/CopyLinkButton'
import { HelpLink } from 'components/HelpLink'
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
    format,
    modality,
    // includes_merged: includeMerged, // TODO: for when we handle checkbox state logic
    metadata_only: metadataOnly
  } = dataset

  const fileItems = [
    modality,
    ...['has_cite_seq_data', 'has_bulk_rna_seq'].filter((key) => dataset[key])
  ].map((key) => getReadableFiles(key))

  const projectsTitlePrefix =
    modality === 'SPATIAL' ? getReadable(modality) : getReadable(format)
  const cardTitle = `${
    metadataOnly ? 'Sample Metadata' : projectsTitlePrefix
  } Download`

  const [mergeObject, setMergeObject] = useState(false)
  const handleChangeMergedObject = () => setMergeObject(!mergeObject)

  return (
    <Box elevation="medium" pad="24px" width="full">
      <Box
        border={{ side: 'bottom' }}
        margin={{ bottom: '24px' }}
        pad={{ bottom: 'medium' }}
      >
        <Text color="brand" size="large" weight="bold">
          {cardTitle}
        </Text>
      </Box>
      <Box justify="between" height="100%">
        <>
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
          {!metadataOnly && (
            <Box direction="row" margin={{ bottom: '24px' }}>
              <CheckBox
                label="Merge samples into one object per project"
                checked={mergeObject}
                onChange={handleChangeMergedObject}
              />
              <HelpLink link={config.links.when_downloading_merged_objects} />
            </Box>
          )}
        </>
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
              <Button label="Download" aria-label="Download" primary />
              {!metadataOnly && <CopyLinkButton computedFile={{}} />}
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

export default DatasetPortalWideDownloadCard
