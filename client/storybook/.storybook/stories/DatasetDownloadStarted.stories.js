import React, { useState } from 'react'
import { Box, Grid } from 'grommet'
import { Button } from 'components/Button'
import { DatasetDownloadStarted } from 'components/DatasetDownloadStarted'
import { Modal, ModalBody } from 'components/Modal'
import { getReadable } from 'helpers/getReadable'

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
  title: 'Components/DatasetDownloadStarted',
  args: {datasets, portalMetadataDataset}
}

const TempMordal = ({ dataset, children }) => {
    const { format, modality, metadata_only: metadataOnly } = dataset
    const cardTitle = `Downloading Portal-wide ${
        metadataOnly ? 'Sample Metadata' :
             `as ${modality === 'SPATIAL'  ? getReadable(modality) : getReadable(format)}`
    }`
    const [showing, setShowing] = useState(false)
    const handleClick = () => {
      setShowing(true)
    }

    return (
      <Box margin="xlarge" align="start">
        <Button
          aria-label={cardTitle}
          flex="grow"
          primary
          label={cardTitle}
          onClick={handleClick}
        />
        <Modal title={cardTitle} showing={showing} setShowing={setShowing}>
          <ModalBody>
            <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
              <Box pad={{ top: 'small' }}>
                {children}
              </Box>
            </Grid>
          </ModalBody>
        </Modal>
      </Box>
    )
  }


export const Default = (args) => (
    <>
      <TempMordal dataset={portalMetadataDataset} {...args}>
        <DatasetDownloadStarted dataset={portalMetadataDataset} {...args} />
      </TempMordal>
      { datasets.map((d) =>
        <TempMordal dataset={d} {...args}>
            <DatasetDownloadStarted dataset={d} {...args} />
        </TempMordal>
      )}
    </>)
