import React from 'react'
import { Box, Text } from 'grommet'
import { useResponsive } from 'hooks/useResponsive'
import { Badge } from 'components/Badge'
import { Button } from 'components/Button'
import { Link } from 'components/Link'
import { WarningText } from 'components/WarningText'
import { getReadable } from 'helpers/getReadable'
import { uniqueArray } from 'helpers/uniqueArray'

// NOTE: Temporarily defined within this component (the existing project card's header component is in a separate file)
const DatasetHeader = ({ dataset, linked = false }) => (
  <>
    {linked ? (
      <Link href="#demo">
        <Text weight="bold" color="brand" size="large">
          {dataset.title}
        </Text>
      </Link>
    ) : (
      <Text weight="bold" color="brand" size="large">
        {dataset.title}
      </Text>
    )}
  </>
)

const Label = ({ label }) => <Text weight="bold">{label}</Text>

// NOTE: This component accepts 'dataset' prop but it's subject to change
// Currently mock data is used via Storybook for development
export const DatasetProjectCard = ({ dataset }) => {
  const { responsive } = useResponsive()
  const projectIds = Object.keys(dataset.data)
  const modalities = ['SINGLE_CELL', 'SPATIAL']
  const downloadOptions = [
    {
      title: 'Data Format',
      value: getReadable(dataset.format)
    },
    {
      title: 'Modality',
      value: modalities.map((modality) => {
        const totalSamples = projectIds.reduce((acc, projectId) => {
          return acc + dataset.data[projectId][modality].length
        }, 0)

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
      value: projectIds.map((projectId) => {
        const {
          includes_bulk: includesBulk,
          merge_single_cell: mergedSingleCell
        } = dataset.data[projectId]
        const hasNoOptions = !includesBulk && !mergedSingleCell

        return (
          <Box key={projectId}>
            {includesBulk && (
              <Text>Include all bulk RNA-seq data in the project</Text>
            )}
            {mergedSingleCell && (
              <Text>Merge single-cell samples into 1 object</Text>
            )}
            {hasNoOptions && <Text>Not Specified</Text>}
          </Box>
        )
      })
    }
  ]

  const samplesDifferenceCount = projectIds.reduce((acc, projectId) => {
    const { SINGLE_CELL, SPATIAL } = dataset.data[projectId]
    const singleCellSamples = uniqueArray(SINGLE_CELL)
    const spatialSamples = uniqueArray(SPATIAL)

    if (singleCellSamples.length === 0 || spatialSamples.length === 0) {
      return 0
    }

    const difference = [
      ...singleCellSamples.filter((sample) => !spatialSamples.includes(sample)),
      ...spatialSamples.filter((id) => !singleCellSamples.includes(id))
    ]
    return acc + difference.length
  }, 0)

  const isSamplesDifference = samplesDifferenceCount > 0

  return (
    <Box elevation="medium" pad="24px" width="full">
      <Box
        border={{ side: 'bottom' }}
        margin={{ bottom: '24px' }}
        pad={{ bottom: '24px' }}
      >
        <DatasetHeader linked dataset={dataset} />
      </Box>
      <Box margin={{ bottom: '24px' }}>
        <Badge badge="Samples">
          <Text size="21px" weight="bold">
            {dataset.downloadable_sample_count} Samples
          </Text>
        </Badge>
      </Box>
      <Box>
        <Box margin={{ bottom: '24px' }}>
          <Label label="Diagnosis" />
          <Text>{dataset.diagnoses_counts}</Text>
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
