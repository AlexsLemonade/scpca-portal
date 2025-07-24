import React from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { config } from 'config'
import { HelpLink } from 'components/HelpLink'
import { InfoText } from 'components/InfoText'
import { Link } from 'components/Link'
import { FormField } from 'components/FormField'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const DatasetProjectAdditionalOptions = ({
  project,
  selectedModalities,
  onExcludeMultiplexedChange,
  onIncludeBulkChange,
  onIncludeMergeChange
}) => {
  const { myDataset, userFormat } = useDatasetManager()

  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    has_multiplexed_data: hasMultiplexed,
    has_single_cell_data: hasSingleCellData,
    includes_merged_sce: includesMergedSce,
    includes_merged_anndata: includesMergedAnnData
  } = project

  const isMergedObjectsAvailable =
    (includesMergedSce || includesMergedAnnData) &&
    (selectedModalities.includes('SINGLE_CELL') ||
      (selectedModalities.length === 0 && hasSingleCellData && !hasMultiplexed))

  // Multiplexed samples are not available for ANN_DATA
  const canExcludeMultiplexed = myDataset.format
    ? myDataset.format !== 'ANN_DATA'
    : userFormat !== 'ANN_DATA'

  // Show the merged objects warning only for multiplexed samples
  const showMergedObjectWarning = !isMergedObjectsAvailable && hasMultiplexed

  return (
    <FormField label="Additional Options" gap="medium" labelWeight="bold">
      <Box direction="row">
        <CheckBox
          label="Merge single-cell samples into 1 object"
          disabled={!isMergedObjectsAvailable}
          onChange={({ target: { checked } }) => onIncludeMergeChange(checked)}
        />
        <HelpLink link={config.links.when_downloading_merged_objects} />
      </Box>
      {showMergedObjectWarning && (
        <InfoText>
          <Text>
            "Merged objects are not available for projects with multiplexed
            samples."{' '}
            <Link
              href={config.links.which_projects_are_merged_objects}
              label="Learn more"
            />
          </Text>
        </InfoText>
      )}

      {hasBulkRnaSeq && (
        <Box direction="row">
          <CheckBox
            label="Include all bulk RNA-seq data in the project"
            onChange={({ target: { checked } }) => onIncludeBulkChange(checked)}
          />
        </Box>
      )}
      {hasMultiplexed && (
        <>
          <Box direction="row">
            <CheckBox
              label="Exclude multiplexed samples"
              disabled={!canExcludeMultiplexed}
              onChange={({ target: { checked } }) =>
                onExcludeMultiplexedChange(checked)
              }
            />
          </Box>
          {!canExcludeMultiplexed && <WarningAnnDataMultiplexed />}
        </>
      )}
    </FormField>
  )
}

export default DatasetProjectAdditionalOptions
