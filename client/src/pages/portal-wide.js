import React from 'react'
import { Anchor, Box, Text } from 'grommet'
import { api } from 'api'
import { HeroBand } from 'components/Band'
import { DatasetPortalWideDownloadCard } from 'components/DatasetPortalWideDownloadCard'
import { useResponsive } from 'hooks/useResponsive'

const PortalWideDownloads = ({ datasets }) => {
  const metadataDatasets = datasets.filter(
    (dataset) => dataset.format === 'METADATA'
  )

  const singleCellExperimentDatasets = datasets.filter(
    (dataset) =>
      dataset.ccdl_modality === 'SINGLE_CELL' &&
      dataset.format === 'SINGLE_CELL_EXPERIMENT'
  )

  const anndataDatasets = datasets.filter(
    (dataset) =>
      dataset.ccdl_modality === 'SINGLE_CELL' && dataset.format === 'ANN_DATA'
  )

  const spatialDatasets = datasets.filter(
    (dataset) => dataset.ccdl_modality === 'SPATIAL'
  )

  const { responsive } = useResponsive()

  return (
    <>
      <HeroBand
        background="dawn"
        width="full"
        align="center"
        pad={{ top: '92px' }}
      >
        <Box
          width={{ max: 'xlarge' }}
          fill
          pad={responsive({ horizontal: 'medium' }, { top: 'large' })}
        >
          <Text size="xxlarge">Portal-wide Downloads</Text>
        </Box>
      </HeroBand>
      <Box width={{ max: 'xlarge' }} pad={{ top: 'xlarge' }} fill>
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
                modality="SINGLE_CELL"
                datasets={singleCellExperimentDatasets}
              />
            </Box>
            <Box pad={{ bottom: 'xlarge' }}>
              <DatasetPortalWideDownloadCard
                title="AnnData (Python) Download"
                modality="SINGLE_CELL"
                datasets={anndataDatasets}
              />
            </Box>
            <Box pad={{ bottom: 'xlarge' }}>
              <DatasetPortalWideDownloadCard
                title="Spatial Download"
                modality="SPATIAL"
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
  const datasetRequest = await api.ccdlDatasets.list({
    ccdl_project_id__isnull: true,
    limit: 100 // default limit is 10, so here we will set it to 100 unless specified
  })

  if (datasetRequest.isOk) {
    return {
      props: { datasets: datasetRequest.response.results }
    }
  }

  return { props: { datasets: null } }
}

export default PortalWideDownloads
