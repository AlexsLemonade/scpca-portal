import React from 'react'
import { genericPortalWideDocsLink } from 'config/ccdlDatasets'
import { Anchor, Box, Grid, Text } from 'grommet'
import { api } from 'api'
import { HeroBandPortalWide } from 'components/Band'
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
      <HeroBandPortalWide
        background="white"
        align="center"
        pad={{ top: '240px' }}
        fill
      >
        <Box
          width={{ max: 'xlarge' }}
          margin={{ top: responsive('-148px', '-132px') }}
          fill
        >
          <Text color="white" size="xxlarge">
            Portal-wide Downloads
          </Text>
        </Box>
      </HeroBandPortalWide>
      <Box width={{ max: 'xlarge' }} fill>
        <Box alignSelf="center" margin={{ top: 'none' }} fill>
          <Box>
            <Text size="medium" margin={{ top: 'small' }}>
              Data from the projects in the ScPCA portal is packaged together
              for your convenience.{' '}
              <Anchor
                target="_blank"
                label={genericPortalWideDocsLink.learnMore.text}
                href={genericPortalWideDocsLink.learnMore.url}
              />
            </Text>
          </Box>

          <Box pad={{ top: 'large', bottom: 'xlarge' }}>
            <Text size="large" margin={{ left: 'medium', bottom: 'medium' }}>
              Metadata Downloads
            </Text>
            <Box>
              <DatasetPortalWideDownloadCard
                title="Sample Metadata Download"
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
          <Grid
            columns={responsive(['auto'], ['1/2', '1/2'])}
            rows={['auto', 'auto']}
            gap="xxlarge"
            pad={{ vertical: 'medium' }}
            width={responsive('100%', '80%')}
          >
            <DatasetPortalWideDownloadCard
              title="SingleCellExperiment (R) Download"
              datasets={singleCellExperimentDatasets}
            />
            <DatasetPortalWideDownloadCard
              title="AnnData (Python) Download"
              datasets={anndataDatasets}
            />
            <DatasetPortalWideDownloadCard
              title="Spatial Download"
              datasets={spatialDatasets}
            />
          </Grid>
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
    const { results: datasets } = datasetRequest.response
    return {
      props: { datasets }
    }
  }

  return { props: { datasets: null } }
}

export default PortalWideDownloads
