import React, { useEffect } from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { useRouter } from 'next/router'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'
import { useResponsive } from 'hooks/useResponsive'
import { getReadable } from 'helpers/getReadable'
import { Button } from 'components/Button'

export const DatasetSamplesTableOptionsHeader = ({
  project,
  includeBulk,
  includeMerge,
  onIncludeBulkChange = () => {},
  onIncludeMergeChange = () => {}
}) => {
  const { back } = useRouter()
  const { myDataset, isProjectIncludeBulk, isProjectMerged, setSamples } =
    useDatasetManager()
  const { selectedSamples } = useDatasetSamplesTable()
  const { responsive } = useResponsive()

  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    includes_merged_sce: includesMergedSce,
    includes_merged_anndata: includesMergedAnnData
  } = project
  const isMergedObjectsAvailable =
    myDataset.format === 'SINGLE_CELL_EXPERIMENT'
      ? includesMergedSce
      : includesMergedAnnData

  const handleSaveAndGoBack = async () => {
    const datasetRequest = await setSamples(project, {
      ...selectedSamples,
      includes_bulk: includeBulk
    })

    if (datasetRequest) {
      back()
    } else {
      // TODO: Error handling
    }
  }

  // Preselect options based on the values in myDataset
  useEffect(() => {
    onIncludeBulkChange(isProjectIncludeBulk(project))
    onIncludeMergeChange(isProjectMerged(project))
  }, [])

  return (
    <>
      <Box
        align="center"
        direction="row"
        justify="between"
        border={{ side: 'bottom', color: 'border-black', size: 'small' }}
        margin={{ bottom: 'large' }}
        pad={{ bottom: 'small' }}
      >
        <Text size="large">View/Edit Samples</Text>
        <Button primary label="Save & Go Back" onClick={handleSaveAndGoBack} />
      </Box>
      <Box
        direction={responsive('column', 'row')}
        gap={responsive('large', 'xlarge')}
      >
        <Box direction="row">
          <Text weight="bold" margin={{ right: 'small' }}>
            Data Format:
          </Text>
          <Text>{getReadable(myDataset.format)}</Text>
        </Box>
        {hasBulkRnaSeq && (
          <CheckBox
            label="Include all bulk RNA-seq data in the project"
            checked={includeBulk}
            onChange={({ target: { checked } }) => onIncludeBulkChange(checked)}
          />
        )}
        {isMergedObjectsAvailable && (
          <CheckBox
            label="Merge single-cell samples into 1 object"
            checked={includeMerge}
            onChange={({ target: { checked } }) =>
              onIncludeMergeChange(checked)
            }
          />
        )}
      </Box>
    </>
  )
}

export default DatasetSamplesTableOptionsHeader
