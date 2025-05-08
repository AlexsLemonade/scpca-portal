import React from 'react'
import { Grid } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { DatasetPortalWideDownloadCard } from 'components/DatasetPortalWideDownloadCard'


const datasets = [
    {
        id: 1,
        format: 'SINGLE_CELL_EXPERIMENT',
        modality: 'SINGLE_CELL',
        has_bulk_rna_seq: true,
        has_cite_seq_data: true,
        includes_merged: true,
        metadata_only: false,
        size_in_bytes: 429496729600
    },
    {
        id: 2,
        format: 'ANN_DATA',
        modality: 'SINGLE_CELL',
        has_bulk_rna_seq: true,
        has_cite_seq_data: true,
        includes_merged: true,
        metadata_only: false,
        size_in_bytes: 966367641600
    },
    {
        id: 3,
        format: 'SINGLE_CELL_EXPERIMENT',
        modality: 'SPATIAL',
        has_bulk_rna_seq: true,
        has_cite_seq_data: false,
        includes_merged: false,
        metadata_only: false,
        size_in_bytes: 429496729600
    }
]

const portalMetadataDataset = {
    id: 1,
    format: null,
    modality: null,
    has_bulk_rna_seq: false,
    has_cite_seq_data: false,
    includes_merged: false,
    metadata_only: true,
    size_in_bytes: 608270
  }


export default {
  title: 'Components/DatasetPortalWideDownloadCard',
  args: {datasets, portalMetadataDataset}
}

export const ProjectsDownload= (args) => {
    const { responsive } = useResponsive()
    return (
    <Grid columns={responsive( '100%' , '420px')} gap="xxlarge">
        { datasets.map((d) =>
            <DatasetPortalWideDownloadCard key={d.id} dataset={d} {...args} />
        )}
    </Grid>)
}

export const PortalMetadataDownload = (args) => (
    <DatasetPortalWideDownloadCard dataset={portalMetadataDataset} {...args}   />
)
