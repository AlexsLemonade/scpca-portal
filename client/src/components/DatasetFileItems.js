import React from 'react'
import { Box } from 'grommet'
import { getReadableFiles } from 'helpers/getReadable'

const Li = ({ children }) => (
  <Box as="li" style={{ display: 'list-item' }}>
    {children}
  </Box>
)

export const DatasetFileItems = ({ dataset }) => {
  return (
    <Box
      as="ul"
      margin={{ top: '0', bottom: 'large' }}
      pad={{ left: 'large' }}
      style={{ listStyle: 'disc' }}
    >
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
    </Box>
  )
}
