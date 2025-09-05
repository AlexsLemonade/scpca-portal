import React from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { config } from 'config'
import { Box, Grid, Text } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { Badge } from 'components/Badge'
import { DatasetAddProjectModal } from 'components/DatasetAddProjectModal'
import { Link } from 'components/Link'
import { Icon } from 'components/Icon'
import { InfoText } from 'components/InfoText'
import { Pill } from 'components/Pill'
import { WarningText } from 'components/WarningText'
import { capitalize } from 'helpers/capitalize'
import { filterOut } from 'helpers/filterOut'
import { getReadable } from 'helpers/getReadable'
import { getReadableModality } from 'helpers/getReadableModality'
import { DownloadOptionsContextProvider } from 'contexts/DownloadOptionsContext'

export const ProjectHeader = ({ project, linked = false }) => {
  const { isProjectAddedToDataset } = useMyDataset()
  const { responsive } = useResponsive()
  const hasUnavailableSample = Number(project.unavailable_samples_count) !== 0
  const unavailableSampleCountText =
    Number(project.unavailable_samples_count) > 1 ? 'samples' : 'sample'

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
              {isProjectAddedToDataset(project) ? (
                <Box
                  direction="row"
                  align="center"
                  gap="small"
                  margin={{ vertical: 'small' }}
                >
                  <Icon color="success" name="Check" />
                  <Text color="success">Added to Dataset</Text>
                </Box>
              ) : (
                <DatasetAddProjectModal project={project} />
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
            label={project.seq_units.map((su) => capitalize(su || ''))}
          />
          <Badge badge="Kit" label={project.technologies.join(', ')} />
          {project.modalities.length > 0 && (
            <Badge
              badge="Modality"
              label={filterOut(project.modalities, 'SINGLE_CELL')
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
