import React from 'react'
import { Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { Badge } from 'components/Badge'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { WarningText } from 'components/WarningText'
import { getReadable } from 'helpers/getReadable'

// NOTE: Temporarily defined within this component (the existing project card's header component is in a separate file)
const DatasetHeader = ({ title }) => (
  <Link href="#demo">
    <Text weight="bold" color="brand" size="large">
      {title}
    </Text>
  </Link>
)

const Label = ({ label }) => <Text weight="bold">{label}</Text>

// NOTE: This component accepts 'dataset' and 'projectId' props but it's subject to change
// Currently mock data is used via Storybook for development
export const DatasetProjectCard = ({ dataset, projectId }) => {
  const { responsive } = useResponsive()

  const {
    data,
    stats: { projects }
  } = dataset

  const { merge_single_cell: mergedSingleCell, includes_bulk: includesBulk } =
    data[projectId]
  const hasNoOptions = !mergedSingleCell && !includesBulk
  const downloadableSamples = projects[projectId].downloadable_sample_count
  const samplesDifferenceCount = projects[projectId].samples_difference_count
  const isSamplesDifference = samplesDifferenceCount > 0

  const downloadOptions = [
    {
      title: 'Data Format',
      value: getReadable(dataset.format)
    },
    {
      title: 'Modality',
      value: ['SINGLE_CELL', 'SPATIAL'].map((modality) => {
        const totalSamples = data[projectId][modality].length
        return (
          <Box key={modality}>
            <Text>
              {totalSamples > 0 && `${getReadable(modality)} (${totalSamples})`}
            </Text>
          </Box>
        )
      })
    },
    {
      title: 'Other Options',
      value: hasNoOptions ? (
        <Text>Not Specified</Text>
      ) : (
        <Box key={projectId}>
          {includesBulk && (
            <Text>Include all bulk RNA-seq data in the project</Text>
          )}
          {mergedSingleCell && (
            <Text>Merge single-cell samples into 1 object</Text>
          )}
        </Box>
      )
    }
  ]

  return (
    <Box elevation="medium" pad="24px" width="full">
      <Box
        border={{ side: 'bottom' }}
        margin={{ bottom: '24px' }}
        pad={{ bottom: '24px' }}
      >
        <DatasetHeader linked title={projects[projectId].title} />
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
          <Text>{projects[projectId].diagnoses_counts}</Text>
        </Box>
        <Box margin={{ bottom: 'xsmall' }}>
          <Label label="Download Options" />
        </Box>
        <Box
          direction={responsive('column', 'row')}
          margin={{ bottom: '24px' }}
        >
          {downloadOptions.map((d) => (
            <Box key={d.title} flex={{ grow: 1 }}>
              <Label label={d.title} />
              {d.value ? (
                <Text>{d.value}</Text>
              ) : (
                <Text italic color="black-tint-30">
                  Not Specified
                </Text>
              )}
            </Box>
          ))}
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
