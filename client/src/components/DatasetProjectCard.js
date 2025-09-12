import React from 'react'
import { Box, Text } from 'grommet'
import { useRouter } from 'next/router'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useMyDataset } from 'hooks/useMyDataset'
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
  const { push, asPath } = useRouter()
  const { saveOriginScrollPosition } = useScrollRestore()
  const { removeProjectById } = useMyDataset()
  const { responsive } = useResponsive()

  const { data } = dataset
  const projectData = data[projectId]
  const diagnoses = dataset.project_diagnoses[projectId]
  const modalityCount = dataset.project_modality_counts[projectId]
  const title = dataset.project_titles[projectId]
  const downloadableSamples = dataset.project_sample_counts[projectId]
  const hasMismatchSamples =
    dataset.modality_count_mismatch_projects.includes(projectId)

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

  const canEditDataset = asPath === '/download'

  const handleViewEditSamples = () => {
    const destination = `${asPath}/${projectId}`
    saveOriginScrollPosition(asPath, destination)
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
        {canEditDataset && (
          <Button
            label="Remove"
            alignSelf={responsive('stretch', 'start')}
            onClick={() => removeProjectById(projectId)}
          />
        )}
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
                <Text key={so}>{so}</Text>
              ))}
              {specifiedOptions.length === 0 && <Text italic>None</Text>}
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
          label={canEditDataset ? 'View/Edit Samples' : 'View Samples'}
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
