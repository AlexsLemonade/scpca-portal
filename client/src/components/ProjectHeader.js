import React from 'react'
import { Box, Text } from 'grommet'
import { Pill } from 'components/Pill'
import { Badge } from 'components/Badge'
import { Link } from 'components/Link'
import { Download } from 'components/Download'
import { getReadable } from 'helpers/getReadable'
import { formatBytes } from 'helpers/formatBytes'
import { capitalize } from 'helpers/capitalize'
import styled, { css } from 'styled-components'

const HeaderBadge = styled(Badge)`
  ${({ label }) =>
    label === '' &&
    css`
      visibility: hidden;
    `}
`

export const ProjectHeader = ({ project, linked = false }) => {
  return (
    <Box>
      <Box direction="row" align="start" justifyContents="between">
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
          pad={{ bottom: 'medium' }}
        >
          <Box align="center" gap="small">
            {project.computed_file && (
              <Download computedFile={project.computed_file} />
            )}
            {project.computed_file && (
              <Text>
                Size: {formatBytes(project.computed_file.size_in_bytes)}
              </Text>
            )}
            {project.has_bulk_rna_seq && (
              <Pill label={getReadable('has_bulk_rna_seq')} />
            )}
          </Box>
        </Box>
      </Box>
      <Box direction="row" justify="between">
        <HeaderBadge
          badge="Samples"
          label={`${project.sample_count} Samples`}
        />
        <HeaderBadge badge="SeqUnit" label={capitalize(project.seq_units)} />
        <HeaderBadge badge="Kit" label={project.technologies} />
        <HeaderBadge badge="Modality" label={project.modalities} />
      </Box>
    </Box>
  )
}

export default ProjectHeader
