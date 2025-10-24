import dynamic from 'next/dynamic'
import React, { useEffect, useState } from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { HelpLink } from 'components/HelpLink'
import { CCDLDatasetDownloadModal } from 'components/CCDLDatasetDownloadModal'
import { DatasetFileItems } from 'components/DatasetFileItems'
import { config } from 'config'
import { CCDLDatasetDownloadModalContextProvider } from 'contexts/CCDLDatasetDownloadModalContext'
import { formatBytes } from 'helpers/formatBytes'

const DatasetCopyLinkButton = dynamic(() => import('./DatasetCopyLinkButton'), {
  ssr: false
})

export const DatasetPortalWideDownloadCard = ({
  title,
  datasets = [],
  metadataOnly = false
}) => {
  const { responsive } = useResponsive()

  const showDownloadSize = !metadataOnly
  const showCopyLinkButton = !metadataOnly

  const [includesMerged, setIncludesMerged] = useState(false)
  const [dataset, setDataset] = useState(
    datasets?.find((d) => !d.includes_files_merged)
  )

  useEffect(() => {
    setDataset(
      datasets?.find((d) => {
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
          <DatasetFileItems dataset={dataset} />
          {datasets?.length > 1 && (
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
            {showDownloadSize && (
              <Text margin={{ bottom: 'small' }} weight="bold">
                Size:{' '}
                {dataset?.computed_file
                  ? formatBytes(dataset?.computed_file?.size_in_bytes)
                  : 'N/A'}
              </Text>
            )}
            <Box
              direction={responsive('column', 'row')}
              gap="24px"
              margin={{ bottom: 'small' }}
            >
              <CCDLDatasetDownloadModalContextProvider datasets={[dataset]}>
                <CCDLDatasetDownloadModal label="Download" />
              </CCDLDatasetDownloadModalContextProvider>
              {showCopyLinkButton && (
                <DatasetCopyLinkButton dataset={dataset} />
              )}
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

export default DatasetPortalWideDownloadCard
