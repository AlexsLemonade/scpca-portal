import { useContext } from 'react'
import { DatasetManagerContext } from 'contexts/DatasetManagerContext'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { uniqueArray } from 'helpers/uniqueArray'

export const useDatasetManager = () => {
  const {
    myDataset,
    setMyDataset,
    datasets,
    setDatasets,
    email,
    setEmail,
    errors,
    setErrors
  } = useContext(DatasetManagerContext)
  const { token, userFormat, setUserFormat } = useScPCAPortal()

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
    setUserFormat(myDataset.format) // Update user preference to match dataset format
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
      return addError(
        'An error occurred while trying to update the dataset',
        dataset
      )
    }

    // TODO: (TBD) To clearly distinguish between unprocessed and processed datasets on the client side,
    // either default the 'start' field to null or add the 'processing_at' field in the serializer.
    // Set only unprocessed dataset to myDataset (temporarily using 'start_at')
    setMyDataset(dataset.start_at != null ? {} : datasetRequest.response)

    return datasetRequest.response
  }

  const clearDataset = async (dataset) =>
    updateDataset({ ...dataset, data: {} })

  const processDataset = async (dataset) => {
    // Token is required for dataset processing
    if (!token) {
      return addError('A valid token is required to update the dataset')
    }

    if (!dataset.email) {
      return addError('An email is required to process the dataset')
    }

    // Save the user email
    setEmail(dataset.email)
    // Set the start flag to true for processing
    return updateDataset({ ...dataset, start: true })
  }

  /* Project-level */
  const addProject = async (project, newProjectData) => {
    const datasetDataCopy = structuredClone(myDataset.data) || {}

    if (datasetDataCopy[project.scpca_id]) {
      console.error('Project already present in myDataset')
    }

    // Make sure data is defined for a new dataset
    datasetDataCopy[project.scpca_id] = newProjectData

    const updatedDataset = {
      ...myDataset,
      data: datasetDataCopy
    }

    return !myDataset.id
      ? createDataset(updatedDataset)
      : updateDataset(updatedDataset)
  }

  const getDatasetProjectData = (project) => {
    // Get the myDataset.data[project.scpca_id] object
    return myDataset?.data?.[project.scpca_id] || {}
  }

  const getProjectDataSamples = (
    project,
    selectedModalities,
    singleCellSamples,
    spatialSamples
  ) => {
    // Populate modality samples for the project data
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
    if (merged) return 'MERGED'

    let projectSamples = samples.filter((s) => s.has_single_cell_data)

    if (excludeMultiplexed) {
      projectSamples = projectSamples.filter((s) => !s.has_multiplexed_data)
    }

    return projectSamples.map((s) => s.scpca_id)
  }

  const getProjectSpatialSamples = (samples) =>
    samples.filter((s) => s.has_spatial_data).map((s) => s.scpca_id)

  const isProjectAddedToDataset = (project) =>
    Object.keys(myDataset?.data || []).includes(project.scpca_id)

  const removeProjectById = (projectId) => {
    const datasetCopy = structuredClone(myDataset)
    delete datasetCopy.data[projectId]

    return updateDataset(datasetCopy)
  }

  /* Sample-level */
  const setSamples = async (project, newProjectData) => {
    const datasetDataCopy = structuredClone(myDataset.data) || {}

    datasetDataCopy[project.scpca_id] = newProjectData

    const updatedDataset = {
      ...myDataset,
      data: datasetDataCopy
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
    datasets,
    email,
    errors,
    userFormat,
    setUserFormat,
    removeError,
    isDatasetDataEmpty,
    clearDataset,
    getDataset,
    processDataset,
    addProject,
    removeProjectById,
    getDatasetProjectData,
    getProjectDataSamples,
    getProjectSingleCellSamples,
    getProjectSpatialSamples,
    isProjectAddedToDataset,
    setSamples,
    getMissingModaliesSamples
  }
}
