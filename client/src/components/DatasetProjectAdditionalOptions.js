import React from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { config } from 'config'
import { HelpLink } from 'components/HelpLink'
import { InfoText } from 'components/InfoText'
import { Link } from 'components/Link'
import { FormField } from 'components/FormField'
import { WarningAnnDataMultiplexed } from 'components/WarningAnnDataMultiplexed'

export const DatasetProjectAdditionalOptions = ({ project }) => {
  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    has_multiplexed_data: hasMultiplexed,
    includes_merged_sce: includesMergedSce,
    includes_merged_anndata: includesMergedAnnData
  } = project

  const isMergedObjectsAvailable = includesMergedSce || includesMergedAnnData
  const isExcludeMultiplexedAvailable = false

  const handleChange = () => {}

  return (
    <FormField label="Additional Options" gap="medium" labelWeight="bold">
      <Box direction="row">
        <CheckBox
          disabled={!isMergedObjectsAvailable}
          label="Merge single-cell samples into 1 object"
          onChange={handleChange}
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
            onChange={handleChange}
          />
        </Box>
      )}
      {hasMultiplexed && (
        <>
          <Box direction="row">
            <CheckBox
              disabled
              label="Exclude multiplexed samples"
              onChange={handleChange}
            />
          </Box>
          {!isExcludeMultiplexedAvailable && <WarningAnnDataMultiplexed />}
        </>
      )}
    </FormField>
  )
}

export default DatasetProjectAdditionalOptions
