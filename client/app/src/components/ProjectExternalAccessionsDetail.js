import React from 'react'
import { Box } from 'grommet'
import { Link } from 'components/Link'

export const ProjectExternalAccessionsDetail = ({
  inline = false,
  externalAccessions = []
}) => {
  // Comma separated list.
  if (inline) {
    return externalAccessions.map(({ accession, url }, i) => (
      <React.Fragment key={accession}>
        {i !== 0 && ', '}
        <Link label={accession} href={url} />
      </React.Fragment>
    ))
  }

  // One external accession per line.
  return externalAccessions.map(({ accession, url }, i) => (
    <Box key={accession} margin={{ top: i ? 'small' : 'none' }}>
      <Link label={accession} href={url} />
    </Box>
  ))
}

export default ProjectExternalAccessionsDetail
