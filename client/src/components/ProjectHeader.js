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
import { accumulateValue } from 'helpers/accumulateValue'
import { config } from 'config'
import { countMultiplexedSamples } from 'helpers/countMultiplexedSamples'
import { InfoText } from './InfoText'
import { WarningText } from './WarningText'

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
      {project.sample_count !== project.downloadable_sample_count && (
        <Box
          border={{ side: 'top' }}
          margin={{ top: 'medium' }}
          pad={{ top: 'medium', bottom: 'small' }}
        >
          <InfoText
            label={`${
              Number(project.sample_count) -
              Number(project.downloadable_sample_count)
            } more samples will be made available soon`}
          />
          {project.has_multiplexed_data && (
            <WarningText
              lineBreak={false}
              text={`${countMultiplexedSamples(
                project.samples
              )} samples are multiplexed.`}
              link={config.links.what_downloading_mulitplexed_sample}
              linkLable="Learn more"
              iconMargin={[0, 0, 0, 0]}
            />
          )}
        </Box>
      )}
    </Box>
  )
}

export default ProjectHeader
