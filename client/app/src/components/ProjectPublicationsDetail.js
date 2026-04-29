import React from 'react'
import { Box, Text } from 'grommet'
import { Link } from 'components/Link'

export const ProjectPublicationsDetail = ({ publications = [] }) => (
  <>
    {publications.map((publication, i) => (
      <Box key={publication.doi} margin={{ top: i ? 'small' : 'none' }}>
        <Text>{publication.citation.replace(publication.doi_url, '')}</Text>
        <Link label={publication.doi_url} href={publication.doi_url} />
      </Box>
    ))}
  </>
)

export default ProjectPublicationsDetail
