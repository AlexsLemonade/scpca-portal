import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { config } from 'config'
import { Box, Grid, Text } from 'grommet'
import { Badge } from 'components/Badge'
import { Download } from 'components/Download'
import { Link } from 'components/Link'
import { InfoText } from 'components/InfoText'
import { Pill } from 'components/Pill'
import { WarningText } from 'components/WarningText'
import { accumulateValue } from 'helpers/accumulateValue'
import { capitalize } from 'helpers/capitalize'
import { formatBytes } from 'helpers/formatBytes'
import { getReadable } from 'helpers/getReadable'

export const ProjectHeader = ({ project, linked = false }) => {
  const { responsive } = useResponsive()
  const hasUnavailableSample = Number(project.unavailable_samples_count) !== 0
  const unavailableSampleCountText =
    Number(project.unavailable_samples_count) > 1 ? 'samples' : 'sample'

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
              <Text weight="bold" color="brand" size="large">
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
            {project.computed_files.length > 0 && (
              <>
                <Download resource={project} />
                <Text>
                  Size:{' '}
                  {formatBytes(
                    accumulateValue(project.computed_files, 'size_in_bytes')
                  )}
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
        <Badge
          badge="Samples"
          label={`${project.downloadable_sample_count} Downloadable Samples`}
        />
        <Badge badge="SeqUnit" label={capitalize(project.seq_units)} />
        <Badge badge="Kit" label={project.technologies} />
        {project.modalities && (
          <Badge badge="Modality" label={project.modalities} />
        )}
      </Grid>

      {hasUnavailableSample && (
        <Box
          border={{ side: 'top' }}
          margin={{ top: 'medium' }}
          pad={{ top: 'medium', bottom: 'small' }}
        >
          <InfoText
            label={`${project.unavailable_samples_count} more ${unavailableSampleCountText} will be made available soon`}
          />
        </Box>
      )}

      {project.has_multiplexed_data && (
        <Box
          border={!hasUnavailableSample ? { side: 'top' } : ''}
          margin={{ top: 'medium' }}
          pad={!hasUnavailableSample ? { top: 'medium' } : ''}
        >
          <WarningText
            lineBreak={false}
            text={`${
              project.multiplexed_sample_count || 'N/A'
            } samples are multiplexed.`}
            link={config.links.how_processed_multiplexed}
            linkLabel="Learn more"
            iconMargin="0"
          />
        </Box>
      )}
    </Box>
  )
}

export default ProjectHeader
