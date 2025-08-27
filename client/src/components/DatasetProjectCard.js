import React from 'react'
import { Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { Badge } from 'components/Badge'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { WarningText } from 'components/WarningText'
import { formatCounts } from 'helpers/formatCounts'
import { getReadable } from 'helpers/getReadable'
import { sortArrayString } from 'helpers/sortArrayString'

const Label = ({ label }) => <Text weight="bold">{label}</Text>

export const DatasetProjectCard = ({ dataset, projectId }) => {
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

  const options = [
    projectData.includes_bulk,
    projectData.SINGLE_CELL === 'MERGED'
  ]
  const hasNoOptions = options.filter((o) => o).length === 0

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
          {sortArrayString(formatCounts(diagnoses)).join(', ')}
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
            {sortArrayString(formatCounts(modalityCount, true)).map((fc) => (
              <Text key={fc}>{fc}</Text>
            ))}
          </Box>
          <Box flex={{ grow: 1 }}>
            <Label label="Other Options" />
            <Box>
              {projectData.includes_bulk && (
                <Text>Include all bulk RNA-seq data in the project</Text>
              )}
              {projectData.SINGLE_CELL === 'MERGED' && (
                <Text>Merge single-cell samples into 1 object</Text>
              )}
              {hasNoOptions && <Text>Not Specified</Text>}
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
          href="#demo"
          alignSelf={responsive('stretch', 'start')}
        />
        {hasMismatchSamples && (
          <WarningText iconMargin="0" iconSize="24px" margin="0">
            <Text>Selected modalities may not be available.</Text>
          </WarningText>
        )}
      </Box>
    </Box>
  )
}

export default DatasetProjectCard
