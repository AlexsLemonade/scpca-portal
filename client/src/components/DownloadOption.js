import React from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'
import { formatBytes } from 'helpers/formatBytes'
import { getDownloadOptionDetails } from 'helpers/getDownloadOptionDetails'

export const DownloadOption = ({
  resource,
  computedFile,
  handleSelectFile
}) => {
  const { header, items, link } = getDownloadOptionDetails(
    resource,
    computedFile
  )
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
        {link && (
          <Box margin={{ top: 'small', bottom: 'medium' }}>
            <Box align="center" direction="row">
              {link.icon && (
                <Icon
                  color={link.icon.color}
                  size="medium"
                  name={link.icon.name}
                />
              )}
              {link.text && (
                <Paragraph margin={{ left: 'small' }}>{link.text}</Paragraph>
              )}
            </Box>
            <Link label={link.label} href={link.url} />
          </Box>
        )}
        <Text>The download consists of the following items:</Text>
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
        <Text>Size: {formatBytes(computedFile.size_in_bytes)}</Text>
      </Box>
      <Box gridArea="footer" margin={{ top: '16px' }}>
        <Box>
          <Button
            primary
            alignSelf="start"
            aria-label={header}
            label={header}
            target="_blank"
            onClick={() => handleSelectFile(computedFile)}
          />
        </Box>
      </Box>
    </Grid>
  )
}

export default DownloadOption
