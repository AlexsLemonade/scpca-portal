import React from 'react'
import { Box, Text } from 'grommet'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { ProjectHeader } from 'components/ProjectHeader'

export const ProjectSearchResult = ({ project }) => {
  const searchDetails = [
    {
      title: 'Diagnosis',
      value: project.diagnoses_counts
    },
    {
      title: 'Abstract',
      value: project.abstract
    },
    {
      title: 'Sample Metadata Fields',
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
          <Button label="View Samples" />
        </Link>
      </Box>
    </Box>
  )
}

export default ProjectSearchResult
