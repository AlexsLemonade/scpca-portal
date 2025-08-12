import { useContext } from 'react'
import { DatasetManagerContext } from 'contexts/DatasetManagerContext'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'

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
  const createDataset = async (dataset) => {
    // TODO: Token check will be removed once the BE is updated
    // Token is only required for processing and downloading
    if (!token) {
      return addError('A valid token is required to create a dataset')
    }

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
    // TODO: Token check will be removed once the BE is updated
    // Token is only required for processing and downloading
    if (!token) {
      return addError('A valid token is required to update the dataset')
    }

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
    // TODO: Token check will be added once the BE is updated
    // Token is required for dataset processing

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

  const getProjectDataSamples = (
    project,
    selectedModalities,
    singleCellSamples,
    spatialSamples
  ) => {
    // Populate modality samples for the project data
    const dataCopy = { ...myDataset.data?.[project.scpca_id] } || {}

    const hasModality = (m) => selectedModalities.includes(m)

    dataCopy.SINGLE_CELL = hasModality('SINGLE_CELL') ? singleCellSamples : []
    dataCopy.SPATIAL = hasModality('SPATIAL') ? spatialSamples : []

    return dataCopy
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

  const getProjectIDs = (dataset) => Object.keys(dataset.data)

  const isProjectAddedToDataset = (project) =>
    Object.keys(myDataset?.data || []).includes(project.scpca_id)

  const removeProject = async (project) => {
    const datasetCopy = structuredClone(myDataset)
    delete datasetCopy.data[project.scpca_id]

    const updatedDataset = await updateDataset(datasetCopy)
    return updatedDataset
  }

  /* Sample-level */
  const setSamples = async (dataset, project, modality, updatedSamples) => {
    // updatedSamples: either sampleIDs[] or 'MERGE'
    const datasetCopy = structuredClone(dataset)

    if (!datasetCopy.data[project.scpca_id]) {
      datasetCopy.data[project.scpca_id] = {}
    }

    datasetCopy.data[project.scpca_id][modality] = updatedSamples

    const updatedDataset = !datasetCopy.id
      ? await createDataset(datasetCopy)
      : await updateDataset(datasetCopy)
    return updatedDataset
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
    clearDataset,
    getDataset,
    processDataset,
    addProject,
    getProjectDataSamples,
    getProjectSingleCellSamples,
    getProjectSpatialSamples,
    getProjectIDs,
    isProjectAddedToDataset,
    removeProject,
    setSamples
  }
}
