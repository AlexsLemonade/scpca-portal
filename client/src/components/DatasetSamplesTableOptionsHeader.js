import React, { useEffect, useRef, useState } from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { config } from 'config'
import { useRouter } from 'next/router'
import { useScrollPosition } from 'hooks/useScrollPosition'
import { useDatasetManager } from 'hooks/useDatasetManager'
import { useDatasetSamplesTable } from 'hooks/useDatasetSamplesTable'
import { useResponsive } from 'hooks/useResponsive'
import { getReadable } from 'helpers/getReadable'
import { Button } from 'components/Button'
import { DatasetChangingMergedProjectModal } from 'components/DatasetChangingMergedProjectModal'
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
  const {
    myDataset,
    isProjectMerged,
    getProjectSingleCellSamples,
    setSamples
  } = useDatasetManager()
  const { selectAllModalitySamples, selectedSamples } = useDatasetSamplesTable()
  const { responsive } = useResponsive()

  // For the changing merged project modal
  const [changeMergedProjectModalOpen, setChangeMergedProjectModalOpen] =
    useState(false)
  const confirmUnmerge = useRef(null)
  const prevSelectedCount = useRef(null) // Previously selected samples count to detect sample deselection
  const newSelectedCount = selectedSamples.SINGLE_CELL.length // Currently selected samples count for comparison

  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    includes_merged_sce: includesMergedSce,
    includes_merged_anndata: includesMergedAnnData
  } = project

  const isMergedObjectsAvailable =
    myDataset.format === 'SINGLE_CELL_EXPERIMENT'
      ? includesMergedSce
      : includesMergedAnnData

  const handleChangeMergedModalCancel = async () => {
    // Reselect any samples that were deselected in the table
    selectAllModalitySamples(
      'SINGLE_CELL',
      getProjectSingleCellSamples(project.samples)
    )
    setChangeMergedProjectModalOpen(false)
  }

  const handleChangeMergedModalContinue = () => {
    confirmUnmerge.current = true
    onIncludeMergeChange(false)
    setChangeMergedProjectModalOpen(false)
  }

  const handleSaveAndGoBack = async () => {
    const datasetRequest = await setSamples(
      project,
      {
        ...selectedSamples,
        includes_bulk: includeBulk
      },
      includeMerge
    )

    if (datasetRequest) {
      setRestoreScrollPosition(asPath)
      back()
    } else {
      // TODO: Error handling
    }
  }

  // Set up prevSelectedCount on initial load
  useEffect(() => {
    if (prevSelectedCount.current === null) {
      prevSelectedCount.current = newSelectedCount
    }
  }, [])

  // Open the modal on sample deselect when:
  // - The user has not confirmed continuing with the unmerge, and
  //   - The project samples are merged, and
  //   - The include merged checkbox is selected
  useEffect(() => {
    if (
      !isProjectMerged(project) ||
      !includeMerge ||
      prevSelectedCount.current === null ||
      confirmUnmerge.current
    ) {
      return
    }

    if (newSelectedCount < prevSelectedCount.current) {
      setChangeMergedProjectModalOpen(true)
    }

    prevSelectedCount.current = newSelectedCount
  }, [newSelectedCount])

  return (
    <>
      <DatasetChangingMergedProjectModal
        hideButton
        nondismissable
        openModal={changeMergedProjectModalOpen}
        onCancel={handleChangeMergedModalCancel}
        onContinue={handleChangeMergedModalContinue}
      />
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
