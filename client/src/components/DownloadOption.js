import React from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'
import { formatBytes } from 'helpers/formatBytes'
import { getDownloadOptionDetails } from 'helpers/getDownloadOptionDetails'
import { isProjectID } from 'helpers/isProjectID'

export const DownloadOption = ({
  resource,
  computedFile,
  handleSelectFile
}) => {
  const { header, items, info } = getDownloadOptionDetails(
    resource,
    computedFile
  )
  const label = isProjectID(resource.scpca_id)
    ? 'Download Project'
    : 'Download Sample'

  return (
    <Grid
      areas={[
        { name: 'header', start: [0, 0], end: [1, 0] },
        { name: 'body', start: [0, 1], end: [1, 1] },
        { name: 'footer', start: [0, 2], end: [1, 2] }
      ]}
      columns={['1/2', '1/2']}
      fill="vertical"
      margin={{ left: '8px', right: '8px' }}
      rows={['auto', '1fr', 'auto']}
    >
      <Box gridArea="header" pad={{ bottom: '8px' }}>
        <Heading level="3" size="small">
          {header}
        </Heading>
      </Box>
      <Box gridArea="body">
        {isProjectID(resource.scpca_id) && info && info.learn_more && (
          <Box margin={{ top: 'small', bottom: 'medium' }}>
            <Box align="center" direction="row">
              {info.learn_more.icon && (
                <Box margin={{ right: 'small' }} pad="small">
                  <Icon
                    color={info.learn_more.icon.color}
                    size={info.learn_more.icon.size}
                    name={info.learn_more.icon.name}
                  />
                </Box>
              )}
              {info.learn_more.text && (
                <Paragraph>
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
        <Text>
          {info && info.text_only && <span>{info.text_only}</span>} The download
          consists of the following items:
        </Text>
        <Box pad="small">
          <ul
            style={{
              listStylePosition: 'inside',
              listStyleType: 'square'
            }}
          >
            {items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Box>
        {info && info.sample_list && (
          <Box margin={{ top: 'small', bottom: 'small' }}>
            <Text>{info.sample_list.text}</Text>
            {resource.additional_metadata.multiplexed_with && (
              <ul style={{ margin: '8px 0 4px 16px' }}>
                {resource.additional_metadata.multiplexed_with.map((item) => (
                  <li key={item} style={{ listStyle: 'inside square' }}>
                    {item}
                  </li>
                ))}
              </ul>
            )}
          </Box>
        )}
        {!isProjectID(resource.scpca_id) && info && info.learn_more && (
          <Box margin={{ bottom: 'medium' }}>
            <Box align="center" direction="row">
              {info.learn_more.icon && (
                <Box margin={{ right: 'small' }} pad="small">
                  <Icon
                    color={info.learn_more.icon.color}
                    size={info.learn_more.icon.size}
                    name={info.learn_more.icon.name}
                  />
                </Box>
              )}
              {info.learn_more.text && (
                <Paragraph>
                  {info.learn_more.text}{' '}
                  {info.learn_more.link && (
                    <Link
                      label={info.learn_more.label}
                      href={info.learn_more.link}
                    />
                  )}
                  .
                </Paragraph>
              )}
            </Box>
          </Box>
        )}
        {info && info.download_project && (
          <Box margin={{ bottom: 'medium' }}>
            <Box align="center" direction="row">
              {info.download_project.icon && (
                <Box margin={{ right: 'small' }} pad="small">
                  <Icon
                    color={info.download_project.icon.color}
                    size={info.download_project.icon.size}
                    name={info.download_project.icon.name}
                  />
                </Box>
              )}
              {info.download_project.text && (
                <Paragraph>
                  {info.download_project.text} <br />
                  {info.download_project.link && (
                    <Link href={info.download_project.link.url}>
                      {info.download_project.link.label}
                    </Link>
                  )}
                </Paragraph>
              )}
            </Box>
          </Box>
        )}

        <Text>Size: {formatBytes(computedFile.size_in_bytes)}</Text>
      </Box>
      <Box gridArea="footer" margin={{ top: '16px' }}>
        <Box>
          <Button
            primary
            alignSelf="start"
            aria-label={resource.computed_files.length > 1 ? header : label}
            label={resource.computed_files.length > 1 ? header : label}
            target="_blank"
            onClick={() => handleSelectFile(computedFile)}
          />
        </Box>
      </Box>
    </Grid>
  )
}

export default DownloadOption
