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
  format,
  onIncludeBulkChange,
  onIncludeMergeChange
}) => {
  const { myDataset } = useDatasetManager()

  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    has_multiplexed_data: hasMultiplexed,
    includes_merged_sce: includesMergedSce,
    includes_merged_anndata: includesMergedAnnData
  } = project

  const isMergedObjectsAvailable =
    (includesMergedSce || includesMergedAnnData) && !hasMultiplexed

  // Multiplexed samples are not available for ANN_DATA
  const canExcludeMultiplexed = myDataset.format
    ? myDataset.format !== 'ANN_DATA'
    : format !== 'ANN_DATA'

  const handleChange = () => {}

  return (
    <FormField label="Additional Options" gap="medium" labelWeight="bold">
      <Box direction="row">
        <CheckBox
          disabled={!isMergedObjectsAvailable}
          label="Merge single-cell samples into 1 object"
          onChange={({ target: { checked } }) => onIncludeMergeChange(checked)}
        />
        <HelpLink link={config.links.when_downloading_merged_objects} />
      </Box>
      {!isMergedObjectsAvailable && (
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
              disabled={!canExcludeMultiplexed}
              label="Exclude multiplexed samples"
              onChange={handleChange}
            />
          </Box>
          {!canExcludeMultiplexed && <WarningAnnDataMultiplexed />}
        </>
      )}
    </FormField>
  )
}

export default DatasetProjectAdditionalOptions
