import React, { useEffect, useState } from 'react'
import { useResponsive } from 'hooks/useResponsive'
import { api } from 'api'
import { config } from 'config'
import { Box, Grid, Text } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { Badge } from 'components/Badge'
import { CCDLDatasetDownloadModal } from 'components/CCDLDatasetDownloadModal'
import { DatasetAddProjectModal } from 'components/DatasetAddProjectModal'
import { InfoText } from 'components/InfoText'
import { InfoViewMyDataset } from 'components/InfoViewMyDataset'
import { Link } from 'components/Link'
import { Pill } from 'components/Pill'
import { WarningText } from 'components/WarningText'
import { capitalize } from 'helpers/capitalize'
import { getReadable } from 'helpers/getReadable'
import { getReadableModality } from 'helpers/getReadableModality'

export const ProjectHeader = ({ project, linked = false }) => {
  const { myDataset, getHasProject, getRemainingProjectSampleIds } =
    useMyDataset()
  const { responsive } = useResponsive()

  // For the dataset action button condition
  const [samples, setSamples] = useState(project.samples) // TODOL: Remove this after API update
  const [remainingSamples, setRemainingSamples] = useState(null) // Populated only if the dataset data in myDataset
  const [isProjectInMyDataset, setIsProjectInMyDataset] = useState(false)

  const hasUnavailableSample = Number(project.unavailable_samples_count) !== 0
  const unavailableSampleCountText =
    Number(project.unavailable_samples_count) > 1 ? 'samples' : 'sample'

  const modalitiesExcludingSingleCell = project.modalities.filter(
    (m) => m !== 'SINGLE_CELL'
  )

  const hasRemainingSamples =
    remainingSamples?.SINGLE_CELL?.length > 0 ||
    remainingSamples?.SPATIAL?.length > 0

  useEffect(() => {
    setIsProjectInMyDataset(getHasProject(project))
  }, [myDataset])

  // TODOL: Remove fetching samples after API update
  // Fetch sample objects on the Browse page only if the project data is in myDataset
  useEffect(() => {
    if (!isProjectInMyDataset) return
    // We get either sample IDs (on Browse) or sample objects (on View Project)
    const isBrowse = typeof project.samples?.[0] !== 'object'

    const asyncFetch = async () => {
      const samplesRequest = await api.samples.list({
        project__scpca_id: project.scpca_id,
        limit: 1000
      })
      if (samplesRequest.isOk) {
        setSamples(samplesRequest.response.results)
      }
    }

    if (isBrowse) asyncFetch()
  }, [isProjectInMyDataset])

  // Get remaining samples not added yet if project data is in myDataset
  useEffect(() => {
    if (!isProjectInMyDataset || !samples) return
    setRemainingSamples(getRemainingProjectSampleIds(project, samples))
  }, [myDataset, samples, isProjectInMyDataset])

  return (
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
          {hasRemainingSamples && (
            <Box margin={{ top: 'medium' }}>
              <InfoViewMyDataset />
            </Box>
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
            <DatasetAddProjectModal
              project={project}
              remainingSamples={remainingSamples}
            />
            <CCDLDatasetDownloadModal label="Download Now" secondary />
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
          label={project.seq_units.map((su) => capitalize(su || '')).join(', ')}
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
          border={!hasUnavailableSample ? { side: 'top' } : false}
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
