import React, { useEffect, useState } from 'react'
import { Anchor, Box, Text } from 'grommet'
// import { api } from 'api'
import { DatasetPortalWideDownloadCard } from 'components/DatasetPortalWideDownloadCard'

// TODO: PortalWideDownloads should accept the arg `{ datasets }`
// which will come from getServerSideProps
const PortalWideDownloads = ({ datasets }) => {
  const metadataDatasets = datasets.filter((dataset) => {
    return dataset.metadata_only === true
  })

  const singleCellExperimentDatasets = datasets.filter(
    (dataset) => dataset.metadata_only === false
  )

  const anndataDatasets = datasets.filter(
    (dataset) => dataset.metadata_only === false
  )

  const spatialDatasets = datasets.filter(
    (dataset) => dataset.metadata_only === false
  )

  return (
    <>
      <Box width={{ max: 'xlarge' }} fill>
        <Box
          alignSelf="start"
          pad={{ left: 'medium' }}
          margin={{ top: 'none' }}
        >
          <Box pad={{ bottom: 'medium' }}>
            <Text size="xlarge" weight="bold">
              Portal-wide Downloads
            </Text>
          </Box>
          <Box pad={{ top: 'large' }}>
            <Text size="medium" margin={{ top: 'small' }}>
              Data from the projects in the ScPCA portal is packaged together
              for your convenience.
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
              <DatasetPortalWideDownloadCard
                title="Sample Metadata Download"
                modality={null}
                datasets={metadataDatasets}
                metadataOnly
              />
            </Box>
          </Box>
        </Box>
      </Box>

      <Box background="dawn" fill align="center">
        <Box width={{ max: 'xlarge' }} fill pad="large">
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
            <Box pad={{ bottom: 'xlarge' }}>
              <DatasetPortalWideDownloadCard
                title="SingleCellExperiment (R) Download"
                modality="SINGLE_CELL_EXPERIMENT"
                datasets={singleCellExperimentDatasets}
              />
            </Box>
            <Box pad={{ bottom: 'xlarge' }}>
              <DatasetPortalWideDownloadCard
                title="AnnData (Python) Download"
                modality="ANN_DATA"
                datasets={anndataDatasets}
              />
            </Box>
            <Box pad={{ bottom: 'xlarge' }}>
              <DatasetPortalWideDownloadCard
                title="Spatial Download"
                modality="SINGLE_CELL_EXPERIMENT"
                datasets={spatialDatasets}
              />
            </Box>
          </Box>
        </Box>
      </Box>
    </>
  )
}

export const getServerSideProps = async () => {
  const datasets = [
    {
      format: null,
      modality: null,
      includes_merged: null,
      metadata_only: true,
      size_in_bytes: 0
    },
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

  // default limit is 10, so here we will set it to 100 unless specified
  // const datasetRequest = await api.ccdlDatasets.list({project_id__isnull: true})

  // if (datasetRequest.isOk) {
  //  return {
  //    props: { datasets: datasetRequest.response }
  //  }
  // }

  // return { props: { datasets: null } }
  return { props: { datasets } }
}

export default PortalWideDownloads
