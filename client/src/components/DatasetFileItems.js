import React from 'react'
import { Box } from 'grommet'
import { getReadableFiles } from 'helpers/getReadable'

const Li = ({ children }) => (
  <Box as="li" style={{ display: 'list-item' }}>
    {children}
  </Box>
)

export const DatasetFileItems = ({
  ccdlModality,
  isMetadataDownload,
  includesFilesBulk,
  includesFilesCiteSeq
}) => {
  return (
    <Box
      as="ul"
      margin={{ top: '0', bottom: 'large' }}
      pad={{ left: 'large' }}
      style={{ listStyle: 'disc' }}
    >
      {isMetadataDownload ? (
        <Li>Sample metadata from all projects</Li>
      ) : (
        <>
          <Li>{getReadableFiles(ccdlModality)}</Li>
          {includesFilesCiteSeq && <Li>CITE-seq data</Li>}
          {includesFilesBulk && <Li>Bulk RNA-Seq data</Li>}
          <Li>Project and Sample Metadata</Li>
        </>
      )}
    </Box>
  )
}
