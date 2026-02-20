import React, { useEffect, useState } from 'react'
import { Box, CheckBox, Text } from 'grommet'
import { config } from 'config'
import { useMyDataset } from 'hooks/useMyDataset'
import { useProjectSamplesTable } from 'hooks/useProjectSamplesTable'
import { useResponsive } from 'hooks/useResponsive'
import { getReadable } from 'helpers/getReadable'
import { DatasetChangingMergedProjectModal } from 'components/DatasetChangingMergedProjectModal'
import { DatasetSaveAndGoBackButton } from 'components/DatasetSaveAndGoBackButton'
import { FormField } from 'components/FormField'
import { HelpLink } from 'components/HelpLink'

export const ProjectSamplesTableOptionsHeader = ({
  project,
  includeBulk,
  includeMerge,
  onIncludeBulkChange = () => {},
  onIncludeMergeChange = () => {}
}) => {
  const { myDataset, isMyDatasetProjectMerged } = useMyDataset()
  const { readOnly, selectAllSingleCellSamples, selectedSamples } =
    useProjectSamplesTable()
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
    !isMyDatasetProjectMerged(project),
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
    // Reselect any single-cell samples that were deselected
    selectAllSingleCellSamples()
    setShowChangeMergedProjectModal(false)
  }

  const handleChangeMergedModalContinue = () => {
    setConfirmUnmerge(true)
    onIncludeMergeChange(false)
    setShowChangeMergedProjectModal(false)
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
          <DatasetSaveAndGoBackButton
            project={project}
            includeBulk={includeBulk}
            includeMerge={includeMerge}
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

export default ProjectSamplesTableOptionsHeader
