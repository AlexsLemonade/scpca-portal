import { useContext } from 'react'
import { DatasetManagerContext } from 'contexts/DatasetManagerContext'
import { api } from 'api'
import { useScPCAPortal } from './useScPCAPortal'

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
  const { token } = useScPCAPortal()

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
    // TODO: Component is reponsible for generating a valid token before request
    // Assumption: If myDataset creation initiated via UI, token should exist.
    if (!token) {
      return addError('A valid token is required to create a dataset')
    }

    // TODO: Component is reponsible for setting format before request
    // Assumption: If myDataset creation initiated via UI, format should exist.
    if (!dataset.format) {
      return addError('A format is required to create a dataset.')
    }

    const datasetRequest = await api.datasets.create(dataset, token)

    if (!datasetRequest.isOk) {
      return addError('An error occurred while trying to create a new dataset.')
    }

    // Add the newly generated dataset ID for historical record
    setDatasets((prev) =>
      prev.includes(datasetRequest.response.id)
        ? prev
        : [...prev, datasetRequest.response.id]
    )

    setMyDataset(datasetRequest.response)

    return datasetRequest.response
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
    // TODO: Component is reponsible for generating a valid token before request
    // Assumption: If myDataset exists, token should exist.
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

    // Set only unprocessed dataset to myDataset
    // NOTE: This change is already included in PR #1376
    setMyDataset(dataset.start_at != null ? {} : datasetRequest.response)

    return datasetRequest.response
  }

  const clearDataset = async (dataset) =>
    updateDataset({ ...dataset, data: {} })

  const processDataset = async (dataset) => {
    // TODO: Component is reponsible for generating a valid token and passing email
    // Assumption: Upon form submission, token and email should exist.
    if (!dataset.email) {
      return addError('An email is required to process the dataset')
    }

    // Save the user email
    setEmail(dataset.email)
    // Set the start flag to true for processing
    return updateDataset({ ...dataset, start: true })
  }

  /* Project-level */
  const addProject = async (dataset, project, projectData) => {
    const datasetCopy = structuredClone(dataset)
    datasetCopy.data[project.scpca_id] = {
      ...(datasetCopy.data[project.scpca_id] || {}),
      ...projectData
    }

    const updatedDataset = !datasetCopy.id
      ? await createDataset(datasetCopy)
      : await updateDataset(datasetCopy)
    return updatedDataset
  }

  const getProjectData = (project, modality, merged = false) => {
    // Returns an object that would populate dataset.data.[project.scpca_id]
    // TODO: Component is reponsible for correctly setting the merged flag, so this check might be unnecessary
    if (merged && modality !== 'SINGLE_CELL') {
      return addError(
        'Merging samples is supported only for Single-cell modality.'
      )
    }

    const hasModality = `has_${modality.toLowerCase()}_data`
    const filteredSamples = merged
      ? 'MERGED'
      : project.samples.filter((s) => s[hasModality]).map((s) => s.scpca_id)

    return { [modality]: filteredSamples }
  }

  const getProjectIDs = (dataset) => Object.keys(dataset.data)

  const removeProject = async (dataset, project) => {
    const datasetCopy = structuredClone(dataset)
    delete datasetCopy.data[project.scpca_id]

    const updatedDataset = await updateDataset(datasetCopy)
    return updatedDataset
  }

  const removeProjectById = (projectId) => {
    const datasetCopy = structuredClone(myDataset)
    delete datasetCopy.data[projectId]

    return updateDataset(datasetCopy)
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
    datasets,
    email,
    errors,
    removeError,
    clearDataset,
    getDataset,
    processDataset,
    addProject,
    getProjectData,
    removeProject,
    removeProjectById,
    getProjectIDs,
    setSamples
  }
}
