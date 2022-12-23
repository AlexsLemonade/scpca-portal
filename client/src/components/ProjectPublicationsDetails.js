import React from 'react'
import { Text } from 'grommet'
import { Link } from 'components/Link'

export const ProjectPublicationsDetail = ({ publications }) => (
  <>
    {publications.map((publication) => (
      <Text key={publication.doi}>
        {publication.citation.replace(publication.doi_url, '')}
        <Link label={publication.doi_url} href={publication.doi_url} />
      </Text>
    ))}
  </>
)

export default ProjectPublicationsDetail
