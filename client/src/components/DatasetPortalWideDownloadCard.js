import React, { useEffect, useState } from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { HelpLink } from 'components/HelpLink'
import { CCDLDatasetDownloadModal } from 'components/CCDLDatasetDownloadModal'
import { CCDLDatasetCopyLinkButton } from 'components/CCDLDatasetCopyLinkButton'
import { config } from 'config'
import { formatBytes } from 'helpers/formatBytes'
import { getReadableFiles } from 'helpers/getReadable'

const Li = ({ children }) => (
  <Box as="li" style={{ display: 'list-item' }}>
    {children}
  </Box>
)

export const DatasetPortalWideDownloadCard = ({
  title,
  datasets = [],
  metadataOnly = false
}) => {
  const { responsive } = useResponsive()

  const [includesMerged, setIncludesMerged] = useState(false)
  const [dataset, setDataset] = useState(
    datasets.find((d) => !d.includes_files_merged)
  )

  useEffect(() => {
    setDataset(
      datasets.find((d) => {
        if (includesMerged) {
          return d.includes_files_merged
        }
        return !d.includes_files_merged
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
            {dataset.format === 'METADATA' ? (
              <Li>Sample metadata from all projects</Li>
            ) : (
              <>
                <Li>{getReadableFiles(dataset.ccdl_modality)}</Li>
                {dataset.includes_files_cite_seq && <Li>CITE-seq data</Li>}
                {dataset.includes_files_bulk && <Li>Bulk RNA-Seq data</Li>}
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
                Size: {formatBytes(dataset?.computed_file?.size_in_bytes)}
              </Text>
            )}
            <Box
              direction={responsive('column', 'row')}
              gap="24px"
              margin={{ bottom: 'small' }}
            >
              <CCDLDatasetDownloadModal
                label="Download"
                initialDatasets={[dataset]}
              />
              {!metadataOnly && <CCDLDatasetCopyLinkButton dataset={dataset} />}
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

export default DatasetPortalWideDownloadCard
