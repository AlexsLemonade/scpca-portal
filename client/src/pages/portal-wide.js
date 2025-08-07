import React from 'react'
import { Anchor, Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { api } from 'api'
import { DatasetPortalWideDownloadCard } from 'components/DatasetPortalWideDownloadCard'

const PortalWideDownloads = () => {
  const { responsive } = useResponsive()

  const metadataDataset = {
    format: null,
    modality: null,
    includes_merged: null,
    metadata_only: true,
    size_in_bytes: 0
  }
  const dataDatasets = [
    {
      format: 'SINGLE_CELL_EXPERIMENT',
      modality: 'SINGLE_CELL',
      includes_merged: false,
      metadata_only: false,
      has_single_cell: true,
      has_cite_seq_data: true,
      has_bulk_rna_seq: true,
      size_in_bytes: 429496729600 // 400 GB
    },
    {
      format: 'ANN_DATA',
      modality: 'SINGLE_CELL',
      includes_merged: false,
      metadata_only: false,
      has_single_cell: true,
      has_cite_seq_data: true,
      has_bulk_rna_seq: true,
      size_in_bytes: 966367641600 // 900 GB
    },
    {
      format: 'SINGLE_CELL_EXPERIMENT',
      modality: 'SPATIAL',
      includes_merged: false,
      metadata_only: false,
      has_spatial_data: true,
      has_bulk_rna_seq: true,
      size_in_bytes: 429496729600 // 400 GB
    }
  ]

  return (
    <>
      <Box alignSelf="start" pad={{ left: 'medium' }} margin={{ top: 'none' }}>
        <Box pad={{ bottom: 'medium' }}>
          <Text size="xlarge" weight="bold">
            Portal-wide Downloads
          </Text>
        </Box>
        <Box pad={{ top: 'large' }}>
          <Text size="medium" margin={{ top: 'small' }}>
            Data from the projects in the ScPCA portal is packaged together for
            your convenience.
            <Anchor
              label=" Please learn more about the portal-wide downloads here."
              href="#"
            />
          </Text>
        </Box>

        <Box pad={{ top: 'large', bottom: 'xlarge' }}>
          <Text size="large" margin={{ bottom: 'medium' }}>
            Metadata Downloads
          </Text>
          <Box>
            <DatasetPortalWideDownloadCard dataset={metadataDataset} />
          </Box>
        </Box>
      </Box>

      <Box background="#EDF7FD">
        <Box pad={{ horizontal: 'large', vertical: 'large' }}>
          <Text size="large" margin={{ bottom: 'small' }}>
            Data Downloads
          </Text>
          <Text size="medium" margin={{ bottom: 'medium' }}>
            Single-cell data from all projects are packaged together by data
            format and whether single-cell samples in each project are merged
            into 1 object.
            <br />A separate spatial only download is also available.
          </Text>
          <Box
            direction="row"
            wrap
            gap="xlarge"
            justify="between"
            pad={{ vertical: 'medium' }}
          >
            {dataDatasets.map((dataset) => (
              <Box
                key={`${dataset.modality}-${dataset.format}`}
                pad={{ bottom: 'xlarge' }}
              >
                <DatasetPortalWideDownloadCard dataset={dataset} />
              </Box>
            ))}
          </Box>
        </Box>
      </Box>
    </>
  )
}

export const getServerSideProps = async () => {
  // default limit is 10, so here we will set it to 100 unless specified
  const datasetRequest = await api.datasets.list()

  if (datasetRequest.isOk) {
    // TODO: Replace with response.results if required (currently returns an array of CCDL datasets)
    const datasets = datasetRequest.response || []
    return {
      props: { datasets }
    }
  }

  return { props: { datasets: null } }
}

export default PortalWideDownloads
