import React from 'react'
import { Box, Text } from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { ProjectHeader } from 'components/ProjectHeader'
import { ProjectAbstractDetail } from 'components/ProjectAbstractDetail'
import { ProjectPublicationsDetail } from 'components/ProjectPublicationsDetail'
import { ProjectExternalAccessionsDetail } from 'components/ProjectExternalAccessionsDetail'

export const ProjectSearchResult = ({ project }) => {
  const searchDetails = [
    {
      title: 'Diagnosis',
      value: project.diagnoses_counts
    },
    {
      title: 'Abstract',
      value: <ProjectAbstractDetail abstract={project.abstract} />
    },
    {
      title: 'Publications',
      value:
        project.publications.length > 0 ? (
          <ProjectPublicationsDetail publications={project.publications} />
        ) : (
          ''
        )
    },
    {
      title: 'Also deposited under',
      value:
        project.external_accessions.length > 0 ? (
          <ProjectExternalAccessionsDetail
            inline
            externalAccessions={project.external_accessions}
          />
        ) : (
          ''
        )
    },
    {
      title: 'Additional Sample Metadata Fields',
      value: project.additional_metadata_keys
    }
  ]
  return (
    <Box elevation="medium" pad="medium" width="full">
      <ProjectHeader linked project={project} />
      <Box border={{ side: 'top' }} margin={{ top: 'medium' }}>
        {searchDetails.map((d) => (
          <Box key={d.title} pad={{ top: 'medium' }}>
            <Text weight="bold">{d.title}</Text>
            {d.value ? (
              <Text>{d.value}</Text>
            ) : (
              <Text italic color="black-tint-30">
                Not Available
              </Text>
            )}
          </Box>
        ))}
      </Box>
      <Box pad={{ top: 'medium' }}>
        <Link href={`/projects/${project.scpca_id}#samples`}>
          <Button label="View Samples" aria-label="View Samples" />
        </Link>
      </Box>
    </Box>
  )
}

export default ProjectSearchResult
