import React from 'react'
import { Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { Badge } from 'components/Badge'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { WarningText } from 'components/WarningText'
import { formatCounts } from 'helpers/formatCounts'
import { getReadable } from 'helpers/getReadable'
import { sortArrayString } from 'helpers/sortArrayString'

const Label = ({ label }) => <Text weight="bold">{label}</Text>

// NOTE: This component accepts 'dataset' and 'projectId' props but it's subject to change
// Currently mock data is used via Storybook for development
export const DatasetProjectCard = ({ dataset, projectId }) => {
  const { responsive } = useResponsive()

  const {
    data,
    stats: { projects }
  } = dataset

  const projectData = data[projectId]
  const { merge_single_cell: mergedSingleCell, includes_bulk: includesBulk } =
    projectData

  const projectStats = projects[projectId]
  const downloadableSamples = projectStats.downloadable_sample_count
  const samplesDifferenceCount = projectStats.samples_difference_count
  const isSamplesDifference = samplesDifferenceCount > 0

  const modalities = ['SINGLE_CELL', 'SPATIAL']
  const options = ['merge_single_cell', 'includes_bulk']
  const hasNoOptions = options.filter((o) => projectData[o]).length === 0

  return (
    <Box elevation="medium" pad="24px" width="full">
      <Box
        border={{ side: 'bottom' }}
        margin={{ bottom: '24px' }}
        pad={{ bottom: '24px' }}
      >
        <Link href="#demo">
          <Text weight="bold" color="brand" size="large">
            {projectStats.title}
          </Text>
        </Link>
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
          {sortArrayString(formatCounts(projectStats.diagnoses_counts)).join(
            ', '
          )}
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
            {modalities.map((modality) => (
              <Text key={modality}>
                {projectData[modality].length > 0 &&
                  `${getReadable(modality)} (${projectData[modality].length})`}
              </Text>
            ))}
          </Box>
          <Box flex={{ grow: 1 }}>
            <Label label="Other Options" />
            <Box>
              {includesBulk && (
                <Text>Include all bulk RNA-seq data in the project</Text>
              )}
              {mergedSingleCell && (
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
        />
        {isSamplesDifference && (
          <WarningText iconMargin="0" iconSize="24px" margin="0">
            <Text>
              Selected modalities may not be available for{' '}
              {samplesDifferenceCount} sample
              {samplesDifferenceCount > 1 ? 's' : ''}.
            </Text>
          </WarningText>
        )}
      </Box>
    </Box>
  )
}

export default DatasetProjectCard
