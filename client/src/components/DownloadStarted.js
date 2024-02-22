import React, { Fragment, useEffect } from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { Button } from 'components/Button'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'
import { formatBytes } from 'helpers/formatBytes'
import { getDefaultComputedFile } from 'helpers/getDefaultComputedFile'
import { getDownloadOptionDetails } from 'helpers/getDownloadOptionDetails'
import { hasMultiple } from 'helpers/hasMultiple'
import { isProjectID } from 'helpers/isProjectID'
import { WarningText } from 'components/WarningText'
import DownloadSVG from '../images/download-folder.svg'

// View when the donwload should have been initiated
export const DownloadStarted = ({
  resource,
  computedFile,
  handleSelectFile,
  recommendedResource,
  handleSelectRecommendedResource
}) => {
  // open the file in a new tab
  const { header, items, info } = getDownloadOptionDetails(
    resource,
    computedFile
  )

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

  // TODO: Remove filter when ANN_DATA lands
  const multipleComputedFiles = hasMultiple(
    resource.computed_files,
    (f) => f.format !== 'ANN_DATA'
  )
  const inlineBorderStyle = multipleComputedFiles
    ? {
        side: 'bottom',
        color: 'border-black',
        size: 'small'
      }
    : ''

  useEffect(() => {}, [resource])

  return (
    <>
      <Grid
        columns={['2/3', '1/3']}
        align="center"
        gap="large"
        pad={{ bottom: 'medium' }}
        border={inlineBorderStyle}
      >
        <Box>
          {multipleComputedFiles && (
            <Heading level="3" size="small">
              {header}
            </Heading>
          )}
          <Paragraph>{startedText}</Paragraph>
          <Box
            direction="row"
            justify="between"
            margin={{ vertical: 'medium' }}
          >
            <Text weight="bold">{idText}</Text>
            <Text weight="bold">Size: {formatBytes(size)}</Text>
          </Box>
          {isProjectID(resource.scpca_id) && info && info.warning_text && (
            <WarningText
              iconSize="24px"
              link={info.warning_text.link.url}
              linkLabel={info.warning_text.link.label}
              text={info.warning_text.text}
            />
          )}
          <Paragraph>
            {info && info.text_only && <span>{info.text_only}</span>} The
            download consists of the following items:
          </Paragraph>
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
          {info && info.texts.multiplexed_with && (
            <Box margin={{ top: 'small', bottom: 'small' }}>
              <Text>{info.texts.multiplexed_with.text}</Text>
              {resource.multiplexed_with && (
                <ul style={{ margin: '8px 0 4px 16px' }}>
                  {resource.multiplexed_with.map((item) => (
                    <li key={item} style={{ listStyle: 'inside square' }}>
                      {item}
                    </li>
                  ))}
                </ul>
              )}
            </Box>
          )}
          {info && info.learn_more && (
            <Paragraph margin={{ bottom: 'small' }}>
              {info.learn_more.text}
              <Link label={info.learn_more.label} href={info.learn_more.url} />.
            </Paragraph>
          )}
          {recommendedResource && handleSelectRecommendedResource && (
            <WarningText iconSize="24px" text={info.warning_text.text}>
              <Box
                onClick={handleSelectRecommendedResource}
                align='="center'
                direction="row"
              >
                <Icon name="Download" />
                &nbsp;&nbsp;
                <Text color="brand">Download Project</Text>
                <Text style={{ fontStyle: 'italic' }}>
                  &nbsp;&nbsp;(Size:{' '}
                  {formatBytes(
                    getDefaultComputedFile(recommendedResource).size_in_bytes
                  )}
                  )
                </Text>
              </Box>
            </WarningText>
          )}
          <Box>
            {responsiveSize !== 'small' && (
              <Paragraph style={{ fontStyle: 'italic' }} color="black-tint-40">
                If your download has not started, please ensure that pop-ups are
                not blocked and try again using the button below:
              </Paragraph>
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
    </>
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
