import React from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { config } from 'config'
import { useRouter } from 'next/router'
import { useScrollPosition } from 'hooks/useScrollPosition'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'
import { useResponsive } from 'hooks/useResponsive'
import { getReadable } from 'helpers/getReadable'
import { Button } from 'components/Button'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'

export const DatasetSamplesTableOptionsHeader = ({
  project,
  includeBulk,
  includeMerge,
  onIncludeBulkChange = () => {},
  onIncludeMergeChange = () => {}
}) => {
  const { back, asPath } = useRouter()
  const { setRestoreScrollPosition } = useScrollPosition()
  const { myDataset, setSamples } = useDatasetManager()
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
      setRestoreScrollPosition(asPath)
      back()
    } else {
      // TODO: Error handling
    }
  }

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
        <FormField
          label={
            <HelpLink
              label={<Text weight="bold">Data Format:</Text>}
              link={config.links.what_downloading}
            />
          }
          direction={responsive('column', 'row')}
          align={responsive('start', 'center')}
        >
          <Text>{getReadable(myDataset.format)}</Text>
        </FormField>
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
