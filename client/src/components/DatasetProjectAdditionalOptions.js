import React from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { config } from 'config'
import { HelpLink } from 'components/HelpLink'
import { InfoText } from 'components/InfoText'
import { Link } from 'components/Link'
import { FormField } from 'components/FormField'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const DatasetProjectAdditionalOptions = ({
  project,
  selectedFormat,
  selectedModalities,
  excludeMultiplexed,
  includeBulk,
  includeMerge,
  onExcludeMultiplexedChange = () => {},
  onIncludeBulkChange = () => {},
  onIncludeMergeChange = () => {}
}) => {
  const { myDataset } = useMyDataset()

  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    has_multiplexed_data: hasMultiplexed,
    includes_merged_sce: includesMergedSce,
    includes_merged_anndata: includesMergedAnnData
  } = project

  const isMergedObjectsAvailable =
    myDataset.format === 'SINGLE_CELL_EXPERIMENT'
      ? includesMergedSce
      : includesMergedAnnData

  const disableMergedObjects =
    (selectedModalities.length > 0 &&
      !selectedModalities.includes('SINGLE_CELL')) ||
    !isMergedObjectsAvailable ||
    myDataset.data?.[project.scpca_id]?.SINGLE_CELL === 'MERGED'

  // Show the merged objects warning only for multiplexed samples
  const showMergedMultiplexedWarning = disableMergedObjects && hasMultiplexed

  // Multiplexed samples are not available for ANN_DATA
  const canExcludeMultiplexed = selectedFormat !== 'ANN_DATA'

  return (
    <FormField label="Additional Options" gap="medium" labelWeight="bold">
      <Box direction="row">
        <CheckBox
          label="Merge single-cell samples into 1 object"
          checked={isMergedObjectsAvailable && includeMerge}
          disabled={disableMergedObjects}
          onChange={({ target: { checked } }) => onIncludeMergeChange(checked)}
        />
        <HelpLink link={config.links.when_downloading_merged_objects} />
      </Box>
      {showMergedMultiplexedWarning && (
        <InfoText>
          <Text>
            Merged objects are not available for projects with multiplexed
            samples.{' '}
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
            checked={hasBulkRnaSeq && includeBulk}
            onChange={({ target: { checked } }) => onIncludeBulkChange(checked)}
          />
        </Box>
      )}
      {hasMultiplexed && (
        <>
          <Box direction="row">
            <CheckBox
              label="Exclude multiplexed samples"
              checked={excludeMultiplexed}
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
