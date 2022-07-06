import React, { Fragment } from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'
import { formatBytes } from 'helpers/formatBytes'
import { config } from 'config'
import { useResponsive } from 'hooks/useResponsive'
import { getDownloadOptionDetails } from 'helpers/getDownloadOptionDetails'
import { isProjectID } from 'helpers/isProjectID'
import DownloadSVG from '../images/download-folder.svg'

// View when the donwload should have been initiated
export const DownloadStarted = ({
  resource,
  computedFile,
  handleSelectFile
}) => {
  // open the file in a new tab
  const { size: responsiveSize } = useResponsive()
  const { size_in_bytes: size, download_url: href } = computedFile
  const isProject = isProjectID(resource.scpca_id)
  const startedText = isProject
    ? 'Your download for the project should have started.'
    : 'Your download for the sample should have started.'
  const idText = `${isProject ? 'Project' : 'Sample'} ID: ${resource.scpca_id}`
  const otherComputedFiles = resource.computed_files.filter(
    (cf) => cf.id !== computedFile.id
  )
  const { header, items, info } = getDownloadOptionDetails(
    resource,
    computedFile
  )

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
            {header}
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
          {info && info.learn_more && (
            <Box margin={{ top: 'small', bottom: 'medium' }}>
              <Box align="center" direction="row">
                {info.learn_more.icon && (
                  <Icon
                    color={info.learn_more.icon.color}
                    size="medium"
                    name={info.learn_more.icon.name}
                  />
                )}
                {info.learn_more.text && (
                  <Paragraph margin={{ left: 'small' }}>
                    {info.learn_more.text} <br />
                    {info.learn_more.link && (
                      <Link
                        label={info.learn_more.label}
                        href={info.learn_more.link}
                      />
                    )}
                  </Paragraph>
                )}
              </Box>
            </Box>
          )}
          <Text>The download consists of the following items:</Text>
          <Box pad="medium">
            <ul
              style={{
                listStylePosition: 'inside',
                listStyleType: 'square'
              }}
            >
              {items.map((item) => (
                <Fragment key={item}>
                  <li>{item}</li>
                </Fragment>
              ))}
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
      {otherComputedFiles.length > 0 && (
        <Grid
          columns={['auto', 'auto']}
          align="center"
          alignContent="between"
          pad={{ vertical: 'medium' }}
        >
          {otherComputedFiles.map((otherComputedFile) => (
            <OtherComputedFile
              key={otherComputedFile.id}
              resource={resource}
              computedFile={otherComputedFile}
              handleSelectFile={handleSelectFile}
            />
          ))}
        </Grid>
      )}
    </span>
  )
}

export default DownloadStarted

const OtherComputedFile = ({ resource, computedFile, handleSelectFile }) => {
  const { header } = getDownloadOptionDetails(resource, computedFile)

  return (
    <>
      <Box>
        <Heading level="3" size="small">
          {header}
        </Heading>
        <Text>Size: {formatBytes(computedFile.size_in_bytes)}</Text>
      </Box>
      <Box>
        <Button
          aria-label={header}
          label={header}
          href=""
          target="_blank"
          onClick={() => handleSelectFile(computedFile)}
        />
      </Box>
    </>
  )
}
