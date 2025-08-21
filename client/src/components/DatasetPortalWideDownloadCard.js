import React, { useEffect, useState } from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { Button } from 'components/Button'
import { CopyLinkButton } from 'components/CopyLinkButton'
import { HelpLink } from 'components/HelpLink'
import { config } from 'config'
import { formatBytes } from 'helpers/formatBytes'
import { getReadableFiles } from 'helpers/getReadable'

const Li = ({ children }) => (
  <Box as="li" style={{ display: 'list-item' }}>
    {children}
  </Box>
)

// NOTE: This component temporaily accepts 'dataset' but it's subject to change
// Currently mock data is used via Storybook for development
export const DatasetPortalWideDownloadCard = ({
  title,
  modality,
  datasets = [],
  metadataOnly = false
}) => {
  const { responsive } = useResponsive()

  const [includesMerged, setIncludesMerged] = useState(false)
  const [dataset, setDataset] = useState(
    // TODO: improve merged check when file items is added to the backend (see below comment)
    datasets.find((d) => !d.ccdl_name.endsWith('MERGED'))
  )

  // TODO: add cite seq, bulk and merged as file items to the backend
  const fileItems = [
    modality,
    ...['has_cite_seq_data', 'has_bulk_rna_seq'].filter((key) => dataset?.[key])
  ].map((key) => getReadableFiles(key))

  useEffect(() => {
    setDataset(
      datasets.find((d) => {
        if (includesMerged) {
          return d.ccdl_name.endsWith('MERGED')
        }
        return !d.ccdl_name.endsWith('MERGED')
      })
    )
  }, [datasets, includesMerged])

  return (
    <Box elevation="medium" background="white" pad="24px" width="full">
      <Box
        border={{ side: 'bottom' }}
        margin={{ bottom: '24px' }}
        pad={{ bottom: 'medium' }}
      >
        <Text color="brand" size="large" weight="bold">
          {title}
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
          {datasets.length > 1 && (
            <Box direction="row" margin={{ bottom: '24px' }}>
              <CheckBox
                label="Merge samples into one object per project"
                checked={includesMerged}
                onChange={({ target: { checked } }) =>
                  setIncludesMerged(checked)
                }
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
                {/* TODO: when computed files are available update to dataset.computedFile.size_in_bytes */}
                Size: {formatBytes(dataset?.stats.uncompressed_size)}
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
