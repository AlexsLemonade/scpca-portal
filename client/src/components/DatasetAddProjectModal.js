import React, { useEffect, useState } from 'react'
import { Box, Grid, Heading } from 'grommet'
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
import { Modal, ModalBody, ModalLoader } from 'components/Modal'

export const DatasetAddProjectModal = ({
  project,
  label = 'Add to Dataset',
  title = 'Add Project to Dataset',
  disabled = false
}) => {
  const {
    myDataset,
    defaultProjectOptions,
    userFormat,
    addProject,
    getProjectDataSamples,
    getProjectSingleCellSamples,
    getProjectSpatialSamples,
    getMissingModaliesSamples
  } = useMyDataset()
  const { responsive } = useResponsive()

  // Modal toggle
  const [showing, setShowing] = useState(false)

  const [modalities, setModalities] = useState([])
  const [format, setFormat] = useState(
    myDataset.format || userFormat || getProjectFormats(project)[0]
  )
  // For additional options
  const [excludeMultiplexed, setExcludeMultiplexed] = useState(false)
  const [includeBulk, setIncludeBulk] = useState(false)
  const [includeMerge, setIncludeMerge] = useState(false)

  // For building the project data for the dataset
  const [projectData, setProjectData] = useState({})
  const [samples, setSamples] = useState(
    // We get either sample IDs (on Browse) or sample objects (on View Project)
    project.samples.filter((s) => s.scpca_id)
  )
  const [singleCellSamples, setSingleCellSamples] = useState([])
  const [spatialSamples, setSpatialSamples] = useState([])

  const [sampleDifference, setSampleDifference] = useState([])

  const canClickAddProject = modalities.length > 0

  const handleAddProject = () => {
    addProject(project, projectData, format)
    setShowing(false)
  }

  // Set additional option values based on defaultProjectOptions and format
  const {
    has_bulk_rna_seq: hasBulkRnaSeq,
    includes_merged_sce: includesMergedSce,
    includes_merged_anndata: includesMergedAnnData
  } = project
  useEffect(() => {
    // Multiplexed samples are not available for ANN_DATA
    setExcludeMultiplexed(format === 'ANN_DATA')
    setIncludeBulk(hasBulkRnaSeq ? defaultProjectOptions.includeBulk : false)
    setIncludeMerge(
      includesMergedSce || includesMergedAnnData
        ? defaultProjectOptions.includeMerge
        : false
    )
    setModalities(
      getProjectModalities(project).filter((m) =>
        defaultProjectOptions.modalities.includes(m)
      )
    )
  }, [defaultProjectOptions, format])

  // Reset the format value on format changes (once empty data)
  useEffect(() => {
    if (!myDataset.format) return
    setFormat(myDataset.format)
  }, [myDataset.format])

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
      setSingleCellSamples([])
    }
  }, [excludeMultiplexed, includeMerge, modalities, samples])

  // Update spatialSamples based on user selections
  useEffect(() => {
    if (modalities.includes('SPATIAL')) {
      setSpatialSamples(getProjectSpatialSamples(samples))
    } else {
      setSpatialSamples([])
    }
  }, [modalities, samples])

  // Calculate missing modality samples
  useEffect(() => {
    setSampleDifference(getMissingModaliesSamples(samples, modalities))
  }, [modalities, samples])

  return (
    <>
      <Button
        aria-label={label}
        flex="grow"
        primary
        label={label}
        disabled={disabled}
        onClick={() => setShowing(true)}
      />
      <Modal title={title} showing={showing} setShowing={setShowing}>
        <ModalBody>
          {!samples.length ? (
            <ModalLoader />
          ) : (
            <Grid columns={['auto']} pad={{ bottom: 'medium' }}>
              <Heading
                level="3"
                size="small"
                margin={{ top: '0', bottom: 'medium' }}
              >
                Download Options
              </Heading>
              <Box pad={{ top: 'small' }}>
                <Box gap="medium" pad={{ bottom: 'medium' }} width="680px">
                  <DatasetDataFormatOptions
                    project={project}
                    format={format}
                    onFormatChange={setFormat}
                  />
                  <DatasetProjectModalityOptions
                    project={project}
                    modalities={modalities}
                    onModalitiesChange={setModalities}
                  />
                  <DatasetProjectAdditionalOptions
                    project={project}
                    selectedFormat={format}
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
                    aria-label={label}
                    label={label}
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
  )
}

export default DatasetAddProjectModal
