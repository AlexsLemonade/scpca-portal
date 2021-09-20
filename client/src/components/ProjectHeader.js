import React from 'react'
import { Box, Text } from 'grommet'
import { Pill } from 'components/Pill'
import { Badge } from 'components/Badge'
import { Link } from 'components/Link'
import { Download } from 'components/Download'
import { getReadable } from 'helpers/getReadable'
import formatBytes from 'helpers/formatBytes'

export const ProjectHeader = ({ project, linked = false }) => {
  return (
    <Box>
      <Box direction="row" align="start" justifyContents="between">
        <Box flex="shrink" pad={{ right: 'medium' }}>
          {linked ? (
            <Link href={`/projects/${project.pi_name}`}>
              <Text weight="bold" color="brand">
                {project.title}
              </Text>
            </Link>
          ) : (
            <Text weight="bold" color="brand" size="large">
              {project.title}
            </Text>
          )}
        </Box>
        <Box gap="small" align="end" width={{ min: '0px' }} flex="grow">
          <Box align="center">
            {project.has_bulk_rna_seq && (
              <Pill label={getReadable('has_bulk_rna_seq')} />
            )}
            <Download computedFile={project.computed_file} />
            <Text>
              Size: {formatBytes(project.computed_file.size_in_bytes)}
            </Text>
          </Box>
        </Box>
      </Box>
      <Box direction="row" justify="between">
        <Badge badge="Samples" label={`${project.sample_count} Samples`} />
        <Badge badge="SeqUnit" label={project.seq_units} />
        <Badge badge="Kit" label={project.technologies} />
        <Badge badge="Modality" label={project.modalities} />
      </Box>
    </Box>
  )
}

export default ProjectHeader
