import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading, Paragraph, Text } from 'grommet'
import { useMyDataset } from 'hooks/useMyDataset'
import { useResponsive } from 'hooks/useResponsive'
import { getProjectModalities } from 'helpers/getProjectModalities'
import { getProjectFormats } from 'helpers/getProjectFormats'
import { api } from 'api'
import { Button } from 'components/Button'
import { DatasetProjectAdditionalOptions } from 'components/DatasetProjectAdditionalOptions'
import { DatasetProjectModalityOptions } from 'components/DatasetProjectModalityOptions'
import { DatasetDataFormatOptions } from 'components/DatasetDataFormatOptions'
import { DatasetWarningMissingSamples } from 'components/DatasetWarningMissingSamples'
import { Icon } from 'components/Icon'
import { InfoViewMyDataset } from 'components/InfoViewMyDataset'
import { Modal, ModalBody, ModalLoader } from 'components/Modal'

/*
This component renders three states:
- Add to Dataset (when no project samples have been added)
- Add Remaining (when some project samples have been added)
- Added to Dataset (when all project samples have been added)
*/

export const DatasetAddProjectModal = ({
  project,
  remainingSamples,
  disabled = false
}) => {
  const {
    myDataset,
    defaultProjectOptions,
    userFormat,
    setUserFormat,
    addProject,
    getMissingModaliesSamples,
    getDatasetProjectData,
    getProjectDataSamples,
    getProjectSingleCellSamples,
    getProjectSpatialSamples
  } = useMyDataset()
  const { responsive } = useResponsive()

  const [showing, setShowing] = useState(false) // Modal toggle
  const [loading, setLoading] = useState(false)

  // For project options
  const [modalities, setModalities] = useState([])
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(false)
  const [includeBulk, setIncludeBulk] = useState(false)
  const [includeMerge, setIncludeMerge] = useState(false)

  // For building the project data for adding to myDataset
  const [projectData, setProjectData] = useState({})
  const [singleCellSamples, setSingleCellSamples] = useState([])
  const [spatialSamples, setSpatialSamples] = useState([])

  const [samples, setSamples] = useState(
    // We get either sample IDs (on Browse) or sample objects (on View Project)
    project.samples.filter((s) => s.scpca_id)
  )
  const [sampleDifference, setSampleDifference] = useState([])

  // For the button states
  const [projectDataInMyDataset, setProjectDataInMyDataset] = useState(null)
  const [hasRemainingSamples, setHasRemainingSamples] = useState(false)
  const addedSingleCellCount = projectDataInMyDataset?.SINGLE_CELL?.length
  const addedSpatialCount = projectDataInMyDataset?.SPATIAL?.length
  const addedSingleCellText =
    projectDataInMyDataset?.SINGLE_CELL === 'MERGED'
      ? 'All single-cell samples as a merged object'
      : `${
          remainingSamples?.SINGLE_CELL.length === 0 ? 'All' : ''
        } ${addedSingleCellCount} samples with single-cell modality`
  const addedSpatialText = `${
    remainingSamples?.SPATIAL.length === 0 ? 'All' : ''
  } ${addedSpatialCount} samples with spatial modality`

  const btnLabel = hasRemainingSamples ? 'Add Remaining' : 'Add to Dataset'
  const modalTitle = hasRemainingSamples
    ? 'Add Remaining Samples to Dataset'
    : 'Add Project to Dataset'

  const canClickAddProject = modalities.length > 0

  const handleAddProject = async () => {
    setLoading(true)
    await addProject(project, projectData, userFormat)
    setLoading(false)
    setShowing(false)
  }

  // Set excludeMultiplexed based on userFormat
  useEffect(() => {
    // Multiplexed samples are not available for ANN_DATA
    setExcludeMultiplexed(userFormat === 'ANN_DATA')
  }, [userFormat])

  // Set default additional options based on project
  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    includes_merged_sce: includesMergedSce,
    includes_merged_anndata: includesMergedAnnData
  } = project
  useEffect(() => {
    const bulkValue = hasRemainingSamples
      ? projectDataInMyDataset?.includes_bulk
      : defaultProjectOptions.includeBulk
    setIncludeBulk(hasBulkRnaSeq ? bulkValue : false)

    const mergedValue = hasRemainingSamples
      ? projectDataInMyDataset?.SINGLE_CELL === 'MERGED'
      : defaultProjectOptions.includeMerge
    setIncludeMerge(
      includesMergedSce || includesMergedAnnData ? mergedValue : false
    )
    setModalities(
      getProjectModalities(project).filter((m) =>
        defaultProjectOptions.modalities.includes(m)
      )
    )
  }, [defaultProjectOptions])

  // Reset Data Fromat dropdown value on modal closes
  useEffect(() => {
    if (!myDataset.format) {
      setUserFormat(getProjectFormats(project)[0])
    } else {
      setUserFormat(myDataset.format)
    }
  }, [myDataset.format, showing])

  // Fetch samples list when modal opens via Browse page
  useEffect(() => {
    const asyncFetch = async () => {
      const samplesRequest = await api.samples.list({
        project__scpca_id: project.scpca_id,
        limit: 1000 // TODO:: 'all' option
      })

      if (samplesRequest.isOk) {
        setSamples(samplesRequest.response.results)
      }
    }
    if (!samples.length && showing) asyncFetch()
  }, [showing])

  //  Get the project data in myDataset for the Add Remaining state
  useEffect(() => {
    setProjectDataInMyDataset(getDatasetProjectData(project))
  }, [myDataset, samples])

  useEffect(() => {
    if (!remainingSamples) return
    setHasRemainingSamples(
      remainingSamples.SINGLE_CELL.length > 0 ||
        remainingSamples.SPATIAL.length > 0
    )
  }, [remainingSamples])

  // Populate the project data for addProject
  useEffect(() => {
    setProjectData({
      ...getProjectDataSamples(
        project,
        modalities,
        singleCellSamples,
        spatialSamples
      ),
      includes_bulk: includeBulk
    })
  }, [includeBulk, modalities, singleCellSamples, spatialSamples])

  // Update singleCellSamples based on user selections
  useEffect(() => {
    if (modalities.includes('SINGLE_CELL')) {
      setSingleCellSamples(
        getProjectSingleCellSamples(samples, includeMerge, excludeMultiplexed)
      )
    } else {
      setSingleCellSamples(projectDataInMyDataset?.SINGLE_CELL || [])
    }
  }, [
    excludeMultiplexed,
    includeMerge,
    modalities,
    samples,
    projectDataInMyDataset
  ])

  // Update spatialSamples based on user selections
  useEffect(() => {
    if (modalities.includes('SPATIAL')) {
      setSpatialSamples(getProjectSpatialSamples(samples))
    } else {
      setSpatialSamples(projectDataInMyDataset?.SPATIAL || [])
    }
  }, [modalities, samples, projectDataInMyDataset])

  // Calculate missing modality samples
  useEffect(() => {
    setSampleDifference(getMissingModaliesSamples(samples, modalities))
  }, [modalities, samples])

  useEffect(() => {
    setLoading(false)
  }, [showing])

  return (
    <>
      {remainingSamples && !hasRemainingSamples ? (
        <Box
          direction="row"
          align="center"
          gap="small"
          margin={{ vertical: 'small' }}
        >
          <Icon color="success" name="Check" />
          <Text color="success">Added to Dataset</Text>
        </Box>
      ) : (
        <>
          <Button
            aria-label={btnLabel}
            flex="grow"
            primary={!hasRemainingSamples}
            secondary={hasRemainingSamples}
            label={btnLabel}
            disabled={disabled}
            onClick={() => setShowing(true)}
          />
          <Modal title={modalTitle} showing={showing} setShowing={setShowing}>
            <ModalBody>
              {!samples.length ? (
                <ModalLoader />
              ) : (
                <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
                  <Heading level="3" size="small" margin={{ top: '0' }}>
                    Download Options
                  </Heading>
                  {hasRemainingSamples && (
                    <>
                      <Box margin={{ vertical: 'medium' }}>
                        <InfoViewMyDataset newTab />
                      </Box>
                      <Paragraph>
                        You've already added the following to My Dataset:
                      </Paragraph>
                      <Box
                        as="ul"
                        margin={{ top: '0' }}
                        pad={{ left: '26px' }}
                        style={{ listStyle: 'disc' }}
                      >
                        {addedSingleCellCount > 0 && (
                          <Box as="li" style={{ display: 'list-item' }}>
                            {addedSingleCellText}
                          </Box>
                        )}

                        {project.has_spatial_data && addedSpatialCount > 0 && (
                          <Box as="li" style={{ display: 'list-item' }}>
                            {addedSpatialText}
                          </Box>
                        )}

                        {projectDataInMyDataset?.includes_bulk && (
                          <Box as="li" style={{ display: 'list-item' }}>
                            All bulk RNA-seq data in the project
                          </Box>
                        )}
                      </Box>
                    </>
                  )}
                  <Box pad={{ top: 'large' }}>
                    <Box gap="medium" pad={{ bottom: 'medium' }} width="680px">
                      <DatasetDataFormatOptions project={project} />
                      <DatasetProjectModalityOptions
                        project={project}
                        remainingSamples={
                          hasRemainingSamples ? remainingSamples : null
                        }
                        modalities={modalities}
                        onModalitiesChange={setModalities}
                      />
                      <DatasetProjectAdditionalOptions
                        project={project}
                        remainingSamples={
                          hasRemainingSamples ? remainingSamples : null
                        }
                        selectedFormat={userFormat}
                        selectedModalities={modalities}
                        excludeMultiplexed={excludeMultiplexed}
                        includeBulk={includeBulk}
                        includeMerge={includeMerge}
                        onExcludeMultiplexedChange={setExcludeMultiplexed}
                        onIncludeBulkChange={setIncludeBulk}
                        onIncludeMergeChange={setIncludeMerge}
                      />
                    </Box>
                    <Box
                      align="center"
                      direction={responsive('column', 'row')}
                      gap="xlarge"
                    >
                      <Button
                        primary
                        aria-label={btnLabel}
                        label={btnLabel}
                        loading={loading}
                        disabled={!canClickAddProject}
                        onClick={handleAddProject}
                      />
                      {sampleDifference.length > 0 && (
                        <DatasetWarningMissingSamples
                          project={project}
                          sampleCount={sampleDifference.length}
                        />
                      )}
                    </Box>
                  </Box>
                </Grid>
              )}
            </ModalBody>
          </Modal>
        </>
      )}
    </>
  )
}

export default DatasetAddProjectModal
