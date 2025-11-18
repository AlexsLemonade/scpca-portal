import { useContext, useEffect, useState } from 'react'
import { MyDatasetContext } from 'contexts/MyDatasetContext'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { allModalities } from 'config/datasets'
import { api } from 'api'
import { uniqueArray } from 'helpers/uniqueArray'

export const useMyDataset = () => {
  const {
    myDataset,
    setMyDataset,
    myDatasetFormat,
    setMyDatasetFormat,
    datasets,
    setDatasets,
    setEmail,
    errors,
    setErrors
  } = useContext(MyDatasetContext)
  const { token, email, userFormat, setUserFormat } = useScPCAPortal()

  const emptyDatasetProjectOptions = {
    includeBulk: false,
    includeMerge: false,
    modalities: []
  }

  const [defaultProjectOptions, setDefaultProjectOptions] = useState(
    emptyDatasetProjectOptions
  )

  // Update the default options for adding additional projects on myDataset changes
  useEffect(() => {
    if (isDatasetDataEmpty) {
      setDefaultProjectOptions({ ...emptyDatasetProjectOptions })
      return
    }

    setDefaultProjectOptions({
      includeBulk: Object.values(myDataset.data).some((p) => p.includes_bulk),
      includeMerge: Object.values(myDataset.data).some(
        (p) => p.SINGLE_CELL === 'MERGED'
      ),
      modalities: allModalities.filter((m) =>
        Object.values(myDataset.data).some(
          (p) => (Array.isArray(p[m]) && p[m].length > 0) || p[m] === 'MERGED'
        )
      )
    })
  }, [myDataset, isDatasetDataEmpty])

  /* Helper */
  const addError = (message, returnValue = null) => {
    // Appends an error message to the errors state for UI components
    console.error(message)
    setErrors((prev) => [...prev, message])
    return returnValue
  }

  const removeError = () => {
    // Removes error message (e..g, by ID)
    // TODO: This method is used by UI components or other hooks (e.g., popups)
  }

  /* Dataset-level */
  const isDatasetDataEmpty =
    !myDataset.data || Object.keys(myDataset.data || {}).length === 0

  const createDataset = async (dataset) => {
    if (!dataset.format) {
      return addError('A format is required to create a dataset.')
    }

    const datasetRequest = await api.datasets.create(dataset, token)

    if (!datasetRequest.isOk) {
      return addError('An error occurred while trying to create a new dataset.')
    }

    const newDataset = datasetRequest.response

    setMyDataset(newDataset)
    setMyDatasetFormat(newDataset.format) // Use to compare format changes on myDataset replace
    setUserFormat(newDataset.format) // Update user preference to match dataset format
    // Add the newly generated dataset ID for historical record
    setDatasets((prev) =>
      prev.includes(newDataset.id) ? prev : [...prev, newDataset.id]
    )

    return newDataset
  }

  const getDataset = async (downloadToken = '') => {
    if (!myDataset.id) return null

    // A valid API token is required for dataset file downloads
    // TODO: Component is reponsible for generating a valid token for file download upon request
    const datasetRequest = await api.datasets.get(myDataset.id, downloadToken)

    if (!datasetRequest.isOk) {
      // TODO:
      // '/dataset': handle fetch and errors via getServerSide
      // '/download': Display the error message to users in the UI
      return addError('An error occurred while trying to fetch the dataset')
    }

    // TODO: non-myDataset will always be fetched via useDataset
    setMyDataset(datasetRequest.response)

    return datasetRequest.response
  }

  const updateDataset = async (dataset) => {
    const datasetRequest = await api.datasets.update(dataset.id, dataset, token)

    if (!datasetRequest.isOk) {
      return addError('An error occurred while trying to update the dataset')
    }

    const { response } = datasetRequest
    // TODO: Determine which field should be used to clear localStorage (e.g., is_started, is_processing, start)
    // Tmporarily using 'start' flag to clear or set the response to myDataset
    setMyDataset(response.start ? {} : response)

    return datasetRequest.response
  }

  const clearDataset = async () => updateDataset({ ...myDataset, data: {} })

  // Return the flags based on a project modality samples' value (SINGLE_CELL, SPATIAL)
  const getModalityState = (value = []) => ({
    isMerged: value === 'MERGED',
    isNonEmptyArray: Array.isArray(value) && value.length > 0,
    isEmptyArray: Array.isArray(value) && value.length === 0
  })

  const getMergedIncludesBulk = (projectId, dataset) =>
    myDataset.data[projectId]?.includes_bulk ||
    dataset.data[projectId]?.includes_bulk

  // Fetch samples for a given project ID and modality
  const getProjectModalitySamples = async (projectId, modality) => {
    const samplesRequest = await api.samples.list({
      project__scpca_id: projectId,
      [`has_${modality.toLowerCase()}_data`]: true,
      limit: 1000 // TODO:: 'all' option
    })

    return samplesRequest.isOk
      ? samplesRequest.response.results.map((s) => s.scpca_id)
      : null
  }

  // Merge project modality samples based on their state (e.g., merged, empty)
  const mergeProjectModalities = async (projectId, modality, dataset) => {
    const original = myDataset.data?.[projectId]?.[modality] || []
    const incoming = dataset.data?.[projectId]?.[modality] || []

    const originalState = getModalityState(original)
    const incomingState = getModalityState(incoming)

    const bothMerged = originalState.isMerged && incomingState.isMerged
    const eitherMerged = originalState.isMerged || incomingState.isMerged
    const eitherEmpty = originalState.isEmptyArray || incomingState.isEmptyArray
    const eitherHasSamples =
      originalState.isNonEmptyArray || incomingState.isNonEmptyArray

    if (bothMerged || (eitherMerged && eitherEmpty)) {
      return 'MERGED'
    }

    // Add all project samples, if one is merged and the other has samples
    if (eitherMerged && eitherHasSamples) {
      return getProjectModalitySamples(projectId, modality)
    }

    return uniqueArray(original, incoming)
  }

  // Handle merging the dataset data into myDataset for the UI
  const getMergeDatasetData = async (dataset) => {
    const projectIds = uniqueArray(
      Object.keys(myDataset.data),
      Object.keys(dataset.data)
    )

    const mergedProjectModaliies = await Promise.all(
      projectIds.map(async (pId) => {
        const modalityData = await Promise.all(
          allModalities.map(async (m) => [
            m,
            await mergeProjectModalities(pId, m, dataset)
          ])
        )
        return [pId, Object.fromEntries(modalityData)]
      })
    )

    // Return null for any merge failure (null samples)
    if (
      mergedProjectModaliies.some(
        ([, data]) => data.SINGLE_CELL === null || data.SPATIAL === null
      )
    ) {
      return null
    }

    return mergedProjectModaliies.reduce((acc, [pId, modalitiesData]) => {
      acc[pId] = {
        ...modalitiesData,
        includes_bulk: getMergedIncludesBulk(pId, dataset)
      }
      return acc
    }, {})
  }

  const processDataset = async () => {
    // Token is required for dataset processing
    if (!token) {
      return addError('A valid token is required to update the dataset')
    }

    if (!email) {
      return addError('An email is required to process the dataset')
    }

    // Save the dataset email
    setEmail(email)
    // Set the start flag to true for processing
    return updateDataset({ ...myDataset, email, start: true })
  }

  /* Project-level */
  const addProject = async (project, newProjectData, format) => {
    const datasetDataCopy = structuredClone(myDataset.data) || {}

    if (datasetDataCopy[project.scpca_id]) {
      console.error('Project already present in myDataset')
    }

    // Make sure data is defined for a new dataset
    datasetDataCopy[project.scpca_id] = newProjectData

    const updatedDataset = {
      ...myDataset,
      data: datasetDataCopy,
      format // Required for a new dataset
    }

    return !myDataset.id
      ? createDataset(updatedDataset)
      : updateDataset(updatedDataset)
  }

  const getDatasetProjectData = (project) => {
    // Get the myDataset.data[project.scpca_id] object
    return myDataset?.data?.[project.scpca_id] || {}
  }

  const getDatasetProjectDataSamples = (project, samples) => {
    const { SINGLE_CELL: singleCell = [], SPATIAL: spatial = [] } =
      getDatasetProjectData(project)

    return {
      SINGLE_CELL:
        singleCell === 'MERGED'
          ? getProjectSingleCellSamples(samples)
          : singleCell,
      SPATIAL: spatial
    }
  }

  const getAddedProjectDataSamples = (project) => {
    // Return an array of all modality samples added to the project data
    const { samples } = project
    const { SINGLE_CELL: singleCell, SPATIAL: spatial } =
      myDataset.data?.[project.scpca_id]

    const singleCellSamples = isProjectMerged(project)
      ? samples.filter((s) => s.has_single_cell_data)
      : samples.filter(
          (s) => s.has_single_cell_data && singleCell.includes(s.scpca_id)
        )
    const spatialSamples = samples.filter(
      (s) => s.has_spatial_data && spatial.includes(s.scpca_id)
    )

    return uniqueArray([...singleCellSamples, ...spatialSamples])
  }

  const getProjectDataSamples = (
    project,
    selectedModalities,
    singleCellSamples,
    spatialSamples
  ) => {
    // Populate modality samples for the project data for addProject
    const datasetProjectDataCopy = structuredClone(
      getDatasetProjectData(project)
    )

    const hasModality = (m) => selectedModalities.includes(m)

    datasetProjectDataCopy.SINGLE_CELL = hasModality('SINGLE_CELL')
      ? singleCellSamples
      : []
    datasetProjectDataCopy.SPATIAL = hasModality('SPATIAL')
      ? spatialSamples
      : []

    return datasetProjectDataCopy
  }

  const getProjectSingleCellSamples = (
    samples,
    merged = false,
    excludeMultiplexed = false
  ) => {
    // Populate SINGLE_CELL value for the project data for addProject
    if (merged) return 'MERGED'

    let projectSamples = samples.filter((s) => s.has_single_cell_data)

    if (excludeMultiplexed) {
      projectSamples = projectSamples.filter((s) => !s.has_multiplexed_data)
    }

    return projectSamples.map((s) => s.scpca_id)
  }

  const getProjectSpatialSamples = (samples) =>
    // Populate SPATIAL value for the project data for addProject
    samples.filter((s) => s.has_spatial_data).map((s) => s.scpca_id)

  const getHasProject = (project) =>
    Object.keys(myDataset?.data || []).includes(project.scpca_id)

  const isProjectIncludeBulk = (project) =>
    myDataset.data?.[project.scpca_id]?.includes_bulk || false

  const isProjectMerged = (project) =>
    myDataset.data?.[project.scpca_id]?.SINGLE_CELL === 'MERGED'

  const removeProjectById = (projectId) => {
    const datasetCopy = structuredClone(myDataset)
    delete datasetCopy.data[projectId]

    return updateDataset(datasetCopy)
  }

  /* Sample-level */
  const setSamples = async (project, newProjectData, format) => {
    const datasetDataCopy = structuredClone(myDataset.data) || {}

    datasetDataCopy[project.scpca_id] = newProjectData

    const updatedDataset = {
      ...myDataset,
      data: datasetDataCopy,
      format // Required for a new dataset
    }

    return !myDataset.id
      ? createDataset(updatedDataset)
      : updateDataset(updatedDataset)
  }

  const getMissingModaliesSamples = (samples, modalities) => {
    const modalityAttributes = {
      SINGLE_CELL: 'has_single_cell_data',
      SPATIAL: 'has_spatial_data'
    }

    const filterdSamples = uniqueArray(
      Object.keys(modalityAttributes)
        .map((m) => samples.filter((s) => s[modalityAttributes[m]]))
        .flat()
    )

    const missingSamples = uniqueArray(
      modalities
        .map((m) => filterdSamples.filter((s) => !s[modalityAttributes[m]]))
        .flat()
    )

    return missingSamples
  }

  return {
    myDataset,
    setMyDataset,
    myDatasetFormat,
    setMyDatasetFormat,
    datasets,
    email,
    errors,
    userFormat,
    setUserFormat,
    removeError,
    defaultProjectOptions,
    isDatasetDataEmpty,
    clearDataset,
    createDataset,
    getDataset,
    updateDataset,
    getMergeDatasetData,
    processDataset,
    addProject,
    removeProjectById,
    getDatasetProjectData,
    getDatasetProjectDataSamples,
    getAddedProjectDataSamples,
    getProjectDataSamples,
    getProjectSingleCellSamples,
    getProjectSpatialSamples,
    getHasProject,
    isProjectIncludeBulk,
    isProjectMerged,
    setSamples,
    getMissingModaliesSamples
  }
}
