import React from 'react'
import { Box, Grid, Heading, Text } from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { formatBytes } from 'helpers/formatBytes'
import { config } from 'config'
import { useResponsive } from 'hooks/useResponsive'
import DownloadSVG from '../images/download-folder.svg'

// computedFile = authenticated ComputedFie with url, whole object
// we will show the other download options off from options from the resource
// View when the donwload should have been initiated
export const DownloadStarted = ({
  resource,
  computedFile,
  switchComputedFile
}) => {
  // open the file in a new tab
  const { size_in_bytes: size, download_url: href } = computedFile
  const startedText = resource.samples
    ? 'Your download for the project should have started.'
    : 'Your download for the sample should have started.'
  const isProject = Boolean(resource.samples)
  const idText = `${isProject ? 'Project' : 'Sample'} ID: ${resource.scpca_id}`
  const isSpatial = computedFile.type.includes('SPATIAL')
  // make context for this
  const singleCellFile = resource.computed_files[0]
  const spatialFile = resource.computed_files[1]

  const { size: responsiveSize } = useResponsive()

  // console.log('computedFile: ', computedFile)

  const handleClick = () => {
    // should be context and switch the selectComputedFile
    switchComputedFile()
  }

  return (
    <span>
      <Grid
        columns={['2/3', '1/3']}
        align="center"
        gap="large"
        pad={{ bottom: 'medium' }}
        border={{
          side: 'bottom',
          color: 'border-black',
          size: 'small'
        }}
      >
        <Box>
          <Heading level="3" size="small">
            {isSpatial ? 'Download Spatial Data' : 'Download Single-cell Data'}
          </Heading>
          <Text>{startedText}</Text>
          <Box
            direction="row"
            justify="between"
            margin={{ vertical: 'medium' }}
          >
            <Text weight="bold">{idText}</Text>
            <Text weight="bold">Size: {formatBytes(size)}</Text>
          </Box>
          <Text>The download consists of the following items:</Text>
          <Box pad="medium">
            <ul
              style={{
                listStylePosition: 'inside',
                listStyleType: 'square'
              }}
            >
              {isSpatial ? (
                <>
                  <li>Spatial data</li>
                  <li>Project and Sample Metadata</li>
                </>
              ) : (
                <>
                  <li>Single-cell data</li>
                  <li>Bulk RNA-seq data</li>
                  <li>CITE-seq data</li>
                  <li>Project and Sample Metadata</li>
                </>
              )}
            </ul>
          </Box>
          <Box pad={{ bottom: 'medium' }}>
            <Text>
              Learn more about what you can expect in your
              <br />
              download file{' '}
              <Link
                href={
                  isProject
                    ? config.links.what_downloading_project
                    : config.links.what_downloading_sample
                }
                label="here"
              />
              .
            </Text>
          </Box>
          <Box>
            {responsiveSize !== 'small' && (
              <Text italic color="black-tint-40">
                If your download has not started, please ensure that pop-ups are
                not blocked and try again using the button below:
              </Text>
            )}
          </Box>
          <Box pad={{ vertical: 'medium' }}>
            <Button
              alignSelf="start"
              aria-label="Try Again"
              label="Try Again"
              href={href}
              target="_blank"
            />
          </Box>
        </Box>
        <Box pad="medium">
          <DownloadSVG width="100%" height="auto" />
        </Box>
      </Grid>
      <Grid columns={['1/2', '1/2']} pad={{ vertical: 'medium' }}>
        <Box>
          <Heading level="3" size="small">
            {isSpatial ? 'Download Single-cell Data' : 'Download Spatial Data'}
          </Heading>
          <Text>
            Size:{' '}
            {formatBytes(
              isSpatial
                ? singleCellFile.size_in_bytes
                : spatialFile.size_in_bytes
            )}
          </Text>
        </Box>
        <Box>
          <Button
            secondary
            aria-label={
              isSpatial ? 'Download Single-cell Data' : 'Download Spatial Data'
            }
            label={
              isSpatial ? 'Download Single-cell Data' : 'Download Spatial Data'
            }
            href=""
            target="_blank"
            onClick={handleClick}
          />
        </Box>
      </Grid>
    </span>
    //   <Grid
    //     columns={['2/3', '1/3']}
    //     align="center"
    //     gap="large"
    //     pad={{ bottom: 'medium' }}
    //     border={{
    //       side: 'bottom',
    //       color: 'border-black',
    //       size: 'small'
    //     }}
    //   >
    //     <Box>
    //       <Text>{startedText}</Text>
    //       <Box
    //         direction="row"
    //         justify="between"
    //         margin={{ vertical: 'medium' }}
    //       >
    //         <Text weight="bold">{idText}</Text>
    //         <Text weight="bold">Size: {formatBytes(size)}</Text>
    //       </Box>
    //       <Box gap="medium">
    //         {responsiveSize !== 'small' && (
    //           <Text italic color="black-tint-40">
    //             If your download has not started, please ensure that pop-ups are
    //             not blocked to enable automatic downloads. You can download now
    //             by using the button below:
    //           </Text>
    //         )}
    //         <Button
    //           alignSelf="start"
    //           label="Download Now"
    //           href={href}
    //           target="_blank"
    //         />
    //       </Box>
    //     </Box>
    //     <Box pad={{ bottom: 'medium', horizontal: 'medium' }}>
    //       <DownloadSVG width="100%" height="auto" />
    //     </Box>
    //   </Grid>
    //   <Box
    //     direction="row"
    //     align="center"
    //     justify="between"
    //     pad={{ top: 'large' }}
    //   >
    //     <Text>
    //       <Link
    //         href={config.links.what_downloading}
    //         label="Read the docs here"
    //       />{' '}
    //       to learn about what you can expect in your download file.
    //     </Text>
    //   </Box>
  )
}

export default DownloadStarted
