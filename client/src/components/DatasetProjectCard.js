import React from 'react'
import { Box, Text } from 'grommet'
import { useRouter } from 'next/router'
import { useScrollPosition } from 'hooks/useScrollPosition'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useResponsive } from 'hooks/useResponsive'
import { Badge } from 'components/Badge'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { WarningText } from 'components/WarningText'
import {
  formatModalityCounts,
  formatDiagnosisCounts
} from 'helpers/formatCounts'
import { getReadable } from 'helpers/getReadable'

const Label = ({ label }) => <Text weight="bold">{label}</Text>

export const DatasetProjectCard = ({ dataset, projectId }) => {
  const { push } = useRouter()
  const { addScrollPosition } = useScrollPosition()
  const { removeProjectById } = useDatasetManager()
  const { responsive } = useResponsive()

  const { data, stats } = dataset
  const projectData = data[projectId]
  const diagnoses = stats.project_diagnoses[projectId]
  const modalityCount = stats.project_modality_counts[projectId]
  const title = stats.project_titles[projectId]
  const downloadableSamples = stats.project_sample_counts[projectId]
  const hasMismatchSamples =
    stats.modality_count_mismatch_projects.includes(projectId)

  const specifiedOptions = [
    {
      label: 'Include all bulk RNA-seq data in the project',
      value: projectData.includes_bulk
    },
    {
      label: 'Merge single-cell samples into 1 object',
      value: projectData.SINGLE_CELL === 'MERGED'
    }
  ]
    .filter((o) => o.value)
    .map((o) => o.label)

  const handleViewEditSamples = () => {
    const source = '/download' // the current route
    const destination = `/download/${projectId}`
    // Save the scroll position before navigating away
    addScrollPosition(source, destination)
    push(destination)
  }

  return (
    <Box elevation="medium" pad="24px" width="full">
      <Box
        direction={responsive('column', 'row')}
        justify={responsive('start', 'between')}
        border={{ side: 'bottom' }}
        gap="large"
        margin={{ bottom: '24px' }}
        pad={{ bottom: '24px' }}
      >
        <Link href={`/projects/${projectId}`} newTab>
          <Text weight="bold" color="brand" size="large">
            {title}
          </Text>
        </Link>
        <Button
          label="Remove"
          alignSelf={responsive('stretch', 'start')}
          onClick={() => removeProjectById(projectId)}
        />
      </Box>
      <Box margin={{ bottom: '24px' }}>
        <Badge badge="Samples">
          <Text size="21px" weight="bold">
            {downloadableSamples} Sample{downloadableSamples > 1 ? 's' : ''}
          </Text>
        </Badge>
      </Box>
      <Box>
        <Box margin={{ bottom: '24px' }}>
          <Label label="Diagnosis" />
          {formatDiagnosisCounts(diagnoses).join(', ')}
        </Box>
        <Box margin={{ bottom: 'xsmall' }}>
          <Label label="Download Options" />
        </Box>
        <Box
          direction={responsive('column', 'row')}
          margin={{ bottom: '24px' }}
        >
          <Box flex={{ grow: 1 }}>
            <Label label="Data Format" />
            <Text>{getReadable(dataset.format)}</Text>
          </Box>
          <Box flex={{ grow: 1 }}>
            <Label label="Modality" />
            {formatModalityCounts(modalityCount).map((fc) => (
              <Text key={fc}>{fc}</Text>
            ))}
          </Box>
          <Box flex={{ grow: 1 }}>
            <Label label="Other Options" />
            <Box>
              {specifiedOptions.map((so) => (
                <Text>{so}</Text>
              ))}
              {specifiedOptions.length === 0 && <Text>Not Specified</Text>}
            </Box>
          </Box>
        </Box>
      </Box>
      <Box
        align={responsive('start', 'center')}
        direction={responsive('column', 'row')}
        gap="large"
      >
        <Button
          label="View/Edit Samples"
          aria-label="View/Edit Samples"
          alignSelf={responsive('stretch', 'start')}
          onClick={handleViewEditSamples}
        />
        {hasMismatchSamples && (
          <WarningText iconMargin="0" iconSize="24px" margin="0">
            <Text>
              Selected modalities may not be available for some samples.
            </Text>
          </WarningText>
        )}
      </Box>
    </Box>
  )
}

export default DatasetProjectCard
