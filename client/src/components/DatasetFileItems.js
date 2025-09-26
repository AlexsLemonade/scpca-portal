import React from 'react'
import { Box } from 'grommet'
import { getReadableFiles } from 'helpers/getReadable'

const Li = ({ children }) => (
  <Box as="li" style={{ display: 'list-item' }}>
    {children}
  </Box>
)

const PortalWideFileItems = ({ dataset }) => {
  return (
    <>
      {dataset?.format === 'METADATA' ? (
        <Li>Sample metadata from all projects</Li>
      ) : (
        <>
          <Li>{getReadableFiles(dataset?.ccdl_modality)}</Li>
          {dataset?.includes_files_cite_seq && <Li>CITE-seq data</Li>}
          {dataset?.includes_files_bulk && <Li>Bulk RNA-Seq data</Li>}
          <Li>Project and Sample Metadata</Li>
        </>
      )}
    </>
  )
}

const ProjectFileItems = ({ dataset }) => {
  const {
    format,
    ccdl_modality: modality,
    includes_files_bulk: hasBulk,
    includes_files_cite_seq: hasCiteSeq,
    includes_files_multiplexed: hasMultiplexed
  } = dataset

  let dataText = 'Single-cell data'
  if (format === 'SINGLE_CELL_EXPERIMENT' && hasCiteSeq) {
    dataText += ', CITE-seq data'
  }

  const singleCellText = `${dataText} as SingleCellExperiment (R)`
  const anndataText = `${dataText} as AnnData (Python)`
  const singleCellFormatText =
    dataset?.format === 'SINGLE_CELL_EXPERIMENT' ? singleCellText : anndataText

  const formatText =
    modality === 'SINGLE_CELL' ? singleCellFormatText : 'Spatial data'

  return (
    <>
      {dataset?.format !== 'METADATA' && (
        <>
          <Li>{formatText}</Li>
          {hasMultiplexed && (
            <Li>Multiplexed single-cell data as SingleCellExperiment (R)</Li>
          )}
          {hasBulk && <Li>Bulk RNA-Seq data</Li>}
          {format === 'ANN_DATA' && hasCiteSeq && (
            <Li>CITE-seq data as AnnData (Python)</Li>
          )}
        </>
      )}
      <Li>Project and Sample Metadata</Li>
    </>
  )
}

export const DatasetFileItems = ({ dataset }) => {
  return (
    <Box
      as="ul"
      margin={{ top: '0', bottom: 'large' }}
      pad={{ left: 'large' }}
      style={{ listStyle: 'disc' }}
    >
      {dataset?.ccdl_project_id ? (
        <ProjectFileItems dataset={dataset} />
      ) : (
        <PortalWideFileItems dataset={dataset} />
      )}
    </Box>
  )
}
