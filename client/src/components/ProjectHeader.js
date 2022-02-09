import React from 'react'
import { Box, Grid, Text } from 'grommet'
import { Pill } from 'components/Pill'
import { Badge } from 'components/Badge'
import { Link } from 'components/Link'
import { Download } from 'components/Download'
import { getReadable } from 'helpers/getReadable'
import { formatBytes } from 'helpers/formatBytes'
import { capitalize } from 'helpers/capitalize'
import { useResponsive } from 'hooks/useResponsive'

export const ProjectHeader = ({ project, linked = false }) => {
  const { responsive } = useResponsive()
  return (
    <Box pad={responsive({ horizontal: 'medium' })}>
      <Box
        direction={responsive('column', 'row')}
        align="start"
        justifyContents="between"
      >
        <Box flex="shrink" pad={{ right: 'medium' }}>
          {linked ? (
            <Link href={`/projects/${project.scpca_id}`}>
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
        <Box
          gap="small"
          align="end"
          width={{ min: '0px' }}
          flex="grow"
          pad={{ top: responsive('medium', 'none'), bottom: 'medium' }}
        >
          <Box align="center" gap="small">
            {project.computed_file && (
              <>
                <Download computedFile={project.computed_file} />
                <Text>
                  Size: {formatBytes(project.computed_file.size_in_bytes)}
                </Text>
              </>
            )}
            {project.has_bulk_rna_seq && (
              <Pill label={`Includes ${getReadable('has_bulk_rna_seq')}`} />
            )}
          </Box>
        </Box>
      </Box>
      <Grid columns={responsive('1', '1/4')} gap={responsive('medium')}>
        <Badge badge="Samples" label={`${project.sample_count} Samples`} />
        <Badge badge="SeqUnit" label={capitalize(project.seq_units)} />
        <Badge badge="Kit" label={project.technologies} />
        <Badge badge="Modality" label={project.modalities} />
      </Grid>
    </Box>
  )
}

export default ProjectHeader
