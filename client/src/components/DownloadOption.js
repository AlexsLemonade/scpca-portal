import React from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { formatBytes } from 'helpers/formatBytes'
import { getDownloadOptionDetails } from 'helpers/getDownloadOptionDetails'
import { isProjectID } from 'helpers/isProjectID'
import { WarningText } from 'components/WarningText'

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
        {isProjectID(resource.scpca_id) && info && info.warning_text && (
          <WarningText
            link={info.warning_text.link.url}
            linkLable={info.warning_text.link.label}
            iconSize="24px"
            text={info.warning_text.text}
          />
        )}
        <Text>
          {info && info.message.text_only && (
            <span>{info.message.text_only}</span>
          )}{' '}
          The download consists of the following items:
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
        {info && info.message.multiplexed_with && (
          <Box margin={{ top: 'small', bottom: 'small' }}>
            <Text>{info.message.multiplexed_with.text}</Text>
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
        {info && info.message.learn_more && (
          <Paragraph margin={{ bottom: 'small' }}>
            {info.message.learn_more.text}
            <Link
              label={info.message.learn_more.label}
              href={info.message.learn_more.url}
            />
            .
          </Paragraph>
        )}
        {!isProjectID(resource.scpca_id) && info && info.warning_text && (
          <WarningText iconSize="24px" text={info.warning_text.text}>
            <Text>TEMP: Download Project</Text>
          </WarningText>
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
