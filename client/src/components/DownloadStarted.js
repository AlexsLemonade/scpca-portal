import React, { Fragment, useState, useEffect } from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { Box, Grid, Paragraph, Text } from 'grommet'
import { Button } from 'components/Button'
import { Icon } from 'components/Icon'
import { Link } from 'components/Link'
import { ProjectAdditionalRestrictions } from 'components/ProjectAdditionalRestrictions'
import { WarningText } from 'components/WarningText'
import { WarningMergedObjects } from 'components/WarningMergedObjects'
import { formatBytes } from 'helpers/formatBytes'
import { getDefaultComputedFile } from 'helpers/getDefaultComputedFile'
import { getDownloadOptionDetails } from 'helpers/getDownloadOptionDetails'
import { api } from 'api'
import DownloadSVG from '../images/download-folder.svg'

// View when the donwload should have been initiated
export const DownloadStarted = ({
  resource,
  computedFile,
  handleSelectFile
}) => {
  // open the file in a new tab
  const { items, info, type, isProject } =
    getDownloadOptionDetails(computedFile)
  const additionalRestrictions = resource.additional_restrictions
  const isMergedObjects = computedFile.s3_key.includes('merged')
  const [recommendedResource, setRecommendedResource] = useState(null)
  const [recommendedFile, setRecommendedFile] = useState(null)

  useEffect(() => {
    // Recommend project when downloading sample
    const fetchRecommended = async () => {
      const { isOk, response } = await api.projects.get(resource.project)
      if (isOk) {
        setRecommendedResource(response)
        const defaultFile = getDefaultComputedFile(response, computedFile)
        setRecommendedFile(defaultFile)
      }
    }

    if (info.fetchRecommended && !recommendedResource) fetchRecommended()
  }, [])

  const { size: responsiveSize } = useResponsive()
  const { size_in_bytes: size, download_url: href } = computedFile
  const startedText = `Your download for the ${type.toLowerCase()} should have started.`
  const idText = `${type} ID: ${resource.scpca_id}`

  return (
    <>
      <Grid
        columns={['2/3', '1/3']}
        align="center"
        gap="large"
        pad={{ bottom: 'medium' }}
      >
        <Box>
          <Paragraph>{startedText}</Paragraph>
          <Box
            direction="row"
            justify="between"
            margin={{ vertical: 'medium' }}
          >
            <Text weight="bold">{idText}</Text>
            <Text weight="bold">Size: {formatBytes(size)}</Text>
          </Box>
          {isProject && info && info.warning_text && (
            <WarningText
              iconSize="24px"
              link={info.warning_text.link.url}
              linkLabel={info.warning_text.link.label}
              text={info.warning_text.text}
            />
          )}
          {isMergedObjects && <WarningMergedObjects />}
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
              {info.learn_more.text}{' '}
              <Link label={info.learn_more.label} href={info.learn_more.url} />.
            </Paragraph>
          )}
          {recommendedResource && handleSelectFile && (
            <WarningText iconSize="24px" text={info.warning_text.text}>
              <Box
                onClick={() =>
                  handleSelectFile(recommendedFile, recommendedResource)
                }
                align='="center'
                direction="row"
              >
                <Icon name="Download" />
                &nbsp;&nbsp;
                <Text color="brand">Download Project</Text>
                <Text style={{ fontStyle: 'italic' }}>
                  &nbsp;&nbsp;(Size:{' '}
                  {formatBytes(recommendedFile.size_in_bytes)})
                </Text>
              </Box>
            </WarningText>
          )}
          {additionalRestrictions && (
            <Box margin={{ vertical: 'medium' }}>
              <ProjectAdditionalRestrictions
                text={additionalRestrictions}
                isModal
              />
            </Box>
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
    </>
  )
}

export default DownloadStarted
