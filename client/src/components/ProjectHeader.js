import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { config } from 'config'
import { Box, Grid, Text } from 'grommet'
import { Badge } from 'components/Badge'
import { DownloadModal } from 'components/DownloadModal'
import { Link } from 'components/Link'
import { InfoText } from 'components/InfoText'
import { Pill } from 'components/Pill'
import { WarningText } from 'components/WarningText'
import { capitalize } from 'helpers/capitalize'
import { getReadable } from 'helpers/getReadable'
import { getReadableModality } from 'helpers/getReadableModality'
import { DownloadOptionsContextProvider } from 'contexts/DownloadOptionsContext'

export const ProjectHeader = ({ project, linked = false }) => {
  const { responsive } = useResponsive()
  const hasUnavailableSample = Number(project.unavailable_samples_count) !== 0
  const unavailableSampleCountText =
    Number(project.unavailable_samples_count) > 1 ? 'samples' : 'sample'

  const modalitiesExcludingSingleCell = project.modalities.filter(
    (m) => m !== 'SINGLE_CELL'
  )

  return (
    <DownloadOptionsContextProvider resource={project}>
      <Box pad={responsive({ horizontal: 'medium' })}>
        <Box
          direction={responsive('column', 'row')}
          align="start"
          justifyContents="between"
          margin={{ bottom: responsive('medium', 'large') }}
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
            pad={{ top: responsive('medium', 'none') }}
          >
            <Box align="center" gap="small">
              {project.computed_files.length > 0 && (
                <DownloadModal label="Download Project" resource={project} />
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
          <Badge
            badge="SeqUnit"
            label={project.seq_units
              .map((su) => capitalize(su || ''))
              .join(', ')}
          />
          <Badge badge="Kit" label={project.technologies.join(', ')} />
          {modalitiesExcludingSingleCell.length > 0 && (
            <Badge
              badge="Modality"
              label={modalitiesExcludingSingleCell
                .map(getReadableModality)
                .join(', ')}
            />
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
    </DownloadOptionsContextProvider>
  )
}

export default ProjectHeader
