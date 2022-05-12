/* eslint-disable no-nested-ternary */
import React from 'react'
import { Box, Grid, Heading, Text } from 'grommet'
import { Button } from 'components/Button'

// View for showing download options without token
export const DownloadOptions = ({
  computedFiles,
  setShowDownloadOptions,
  setPublicComputedFile
}) => {
  // const { size: responsiveSize } = useResponsive()
  const handleClick = (type) => {
    selectType(type)
    setShowDownloadOptions(false)
  }

  const selectType = (type) => {
    switch (type) {
      case 'singlecell':
        setPublicComputedFile(computedFiles[0])
        break
      case 'spatial':
        setPublicComputedFile(computedFiles[1])
        break
      default:
        setPublicComputedFile(null)
        break
    }
  }

  return (
    <Grid columns={['1/2', '1/2']} gap="large" pad={{ bottom: 'medium' }}>
      <Grid
        columns={['1/2', '1/2']}
        areas={[
          { name: 'header', start: [0, 0], end: [1, 0] },
          { name: 'body', start: [0, 1], end: [1, 1] },
          { name: 'footer', start: [0, 2], end: [1, 2] }
        ]}
        border={{
          side: 'right',
          color: 'border-black',
          size: 'small'
        }}
        pad={{ left: '16px', right: '32px' }}
        rows={['auto', '1fr', 'auto']}
      >
        <Box gridArea="header">
          <Heading level="3" size="small">
            Download Single-cell Data
          </Heading>
        </Box>
        <Box gridArea="body">
          <Text>The download consists of the following items:</Text>
          <Box pad="small">
            <ul
              style={{
                listStylePosition: 'inside',
                listStyleType: 'square'
              }}
            >
              <li>Single-cell data</li>
              <li>Bulk RNA-seq data</li>
              <li>CITE-seq data</li>
              <li>Project and Sample Metadata</li>
            </ul>
          </Box>
          <Text>Size: 900 MB</Text>
        </Box>
        <Box gridArea="footer" margin={{ top: '16px' }}>
          <Box>
            <Button
              primary
              alignSelf="start"
              aria-label="Download Single-cell Data"
              label="Download Single-cell Data"
              target="_blank"
              onClick={() => handleClick('singlecell')}
            />
          </Box>
        </Box>
      </Grid>

      <Grid
        areas={[
          { name: 'header', start: [0, 0], end: [1, 0] },
          { name: 'body', start: [0, 1], end: [1, 1] },
          { name: 'footer', start: [0, 2], end: [1, 2] }
        ]}
        columns={['1/2', '1/2']}
        pad={{ left: '16px', right: '32px' }}
        rows={['auto', '1fr', 'auto']}
      >
        <Box gridArea="header">
          <Heading level="3" size="small">
            Download Spatial Data
          </Heading>
        </Box>
        <Box gridArea="body">
          <Text>The download consists of the following items:</Text>
          <Box pad="small">
            <ul
              style={{
                listStylePosition: 'inside',
                listStyleType: 'square'
              }}
            >
              <li>Spatial data</li>
              <li>Project and Sample Metadata</li>
            </ul>
          </Box>
          <Text>Size: 350 MB</Text>
        </Box>
        <Box gridArea="footer" margin={{ top: '16px' }}>
          <Box>
            <Button
              primary
              alignSelf="start"
              aria-label="Download Spatial Data"
              label="Download Spatial Data"
              target="_blank"
              onClick={() => handleClick('spatial')}
            />
          </Box>
        </Box>
      </Grid>
    </Grid>
  )
}

export default DownloadOptions
