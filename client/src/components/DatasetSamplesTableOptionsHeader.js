import React, { useEffect, useState } from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { config } from 'config'
import { useRouter } from 'next/router'
import { useScrollRestore } from 'hooks/useScrollRestore'
import { useMyDataset } from 'hooks/useMyDataset'
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
  readOnly = false,
  onIncludeBulkChange = () => {},
  onIncludeMergeChange = () => {}
}) => {
  const { asPath, back } = useRouter()
  const { setRestoreFromDestination } = useScrollRestore()
  const {
    myDataset,
    isProjectMerged,
    getProjectSingleCellSamples,
    setSamples
  } = useMyDataset()
  const { selectAllModalitySamples, selectedSamples } = useDatasetSamplesTable()
  const { responsive } = useResponsive()

  // For the changing merged project modal visibility and conditions
  const [confirmUnmerge, setConfirmUnmerge] = useState(false)
  const [prevSelectedCount, setPrevSelectedCount] = useState(null) // Count for previously selected samples to detect sample deselection
  const noPrevSelectedSamples = prevSelectedCount === null
  const newSelectedCount = selectedSamples.SINGLE_CELL.length // Count for currently selected samples for comparison
  const [showChangeMergedProjectModal, setShowChangeMergedProjectModal] =
    useState(false)

  const title = !readOnly ? 'View/Edit Samples' : 'View Samples'

  // The modal should be hidden when:
  // - Project is not merged
  // - Include merged option is deselected
  // - User has already confirmed unmerge action
  // - Previously selected samples count is not initialized yet
  const hideChangeMergedProjectModal = [
    !isProjectMerged(project),
    !includeMerge,
    confirmUnmerge,
    noPrevSelectedSamples
  ].some(Boolean)

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
    setShowChangeMergedProjectModal(false)
  }

  const handleChangeMergedModalContinue = () => {
    setConfirmUnmerge(true)
    onIncludeMergeChange(false)
    setShowChangeMergedProjectModal(false)
  }

  const handleSaveAndGoBack = async () => {
    const newSamplesToAdd = {
      ...selectedSamples,
      ...(includeMerge && { SINGLE_CELL: 'MERGED' })
    }

    const datasetRequest = await setSamples(project, {
      ...newSamplesToAdd,
      includes_bulk: includeBulk
    })

    if (datasetRequest) {
      const source = asPath.replace(/\/SCPCP\d{6}/, '') // The page to navigating back to
      setRestoreFromDestination(source)
      back()
    } else {
      // TODO: Error handling
    }
  }

  // Set up prevSelectedCount on initial load
  useEffect(() => {
    if (noPrevSelectedSamples) {
      setPrevSelectedCount(newSelectedCount)
    }
  }, [])

  // Open the changing merged project modal on sample deselect
  useEffect(() => {
    if (hideChangeMergedProjectModal) {
      return
    }

    if (newSelectedCount < prevSelectedCount) {
      setShowChangeMergedProjectModal(true)
    }

    setPrevSelectedCount(newSelectedCount)
  }, [newSelectedCount])

  return (
    <>
      <DatasetChangingMergedProjectModal
        hideButton
        nondismissable
        openModal={showChangeMergedProjectModal}
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
        <Text size="large">{title}</Text>
        {!readOnly && (
          <Button
            primary
            label="Save & Go Back"
            onClick={handleSaveAndGoBack}
          />
        )}
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
            disabled={readOnly}
            onChange={({ target: { checked } }) => onIncludeBulkChange(checked)}
          />
        )}
        {isMergedObjectsAvailable && (
          <CheckBox
            label="Merge single-cell samples into 1 object"
            checked={includeMerge}
            disabled={readOnly}
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
