import { useContext } from 'react'
import { DatasetManagerContext } from 'contexts/DatasetManagerContext'
import { api } from 'api'
import { useScPCAPortal } from './useScPCAPortal'

export const useDatasetManager = () => {
  const { myDataset, setMyDataset, datasets, setDatasets, email, setEmail } =
    useContext(DatasetManagerContext)
  const { token } = useScPCAPortal()

  /* Dataset-level */
  const isMyDatasetId = (dataset) =>
    myDataset.id !== null && dataset.id === myDataset.id

  const createDataset = async (dataset) => {
    // TODO: Component is reponsible for generating a valid token before request
    // Assumption: If myDataset creation initiated via UI, token should exist.
    if (!token) {
      console.error('A valid token is required to create a dataset')
      throw new Error('Token required') // if necessary
    }

    // TODO: Component is reponsible for setting format before request
    // Assumption: If myDataset creation initiated via UI, format should exist.
    if (!dataset.format) {
      console.error('A format is required to create a dataset.')
      throw new Error('Format required') // if necessary
    }

    const datasetRequest = await api.datasets.create(dataset, token)

    if (!datasetRequest.isOk) {
      console.error('An error occurred while trying to create a new dataset.')
      // TODO: Should we display this error message to users in the UI?
      // e.g., show notification popup
      return null
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

  const getDataset = async (dataset, downloadToken = '') => {
    // A valid API token is required for dataset file downloads
    // TODO: Component is reponsible for generating a valid token for file download upon request
    const datasetRequest = await api.datasets.get(dataset.id, downloadToken)

    if (!datasetRequest.isOk) {
      // TODO:
      // '/dataset': handle fetch and errors via getServerSide
      // '/download': Should we display this error message to users in the UI?
      // e.g., show notification popup
      console.error('An error occurred while trying to fetch the dataset')
    }

    // This method is used for both myDataset and non-myDataset
    // Update myDataset if this dataset is the user's
    if (isMyDatasetId(dataset)) {
      setMyDataset(datasetRequest.response)
    }

    return datasetRequest.response
  }

  const updateDataset = async (dataset) => {
    // TODO: Component is reponsible for generating a valid token before request
    // Assumption: If myDataset exists, token should exist.
    if (!token) {
      console.error('A valid token is required to update the dataset')
      throw new Error('Token required') // if necessary
    }

    const datasetRequest = await api.datasets.update(dataset.id, dataset, token)

    if (!datasetRequest.isOk) {
      console.error('An error occurred while trying to update the dataset')
      // TODO: Should we display this error message to users in the UI?
      // e.g., show notification popup
      return dataset
    }

    // Set only unprocessed dataset to myDataset
    setMyDataset(dataset.start != null ? null : datasetRequest.response)

    return datasetRequest.response
  }

  const clearDataset = async (dataset) =>
    updateDataset({ ...dataset, data: {} })

  const processDataset = async (dataset) => {
    // TODO: Component is reponsible for generating a valid token and passing email
    // Assumption: Upon form submission, token and email should exist.
    if (!dataset.email) {
      console.error('An email is required to process the dataset')
      throw new Error('Email is required') // if necessary
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
      console.error('Samples cannot be merged')
      throw new Error('Merged object supported for Single-cell only') // if necessary
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
    clearDataset,
    getDataset,
    processDataset,
    addProject,
    getProjectData,
    removeProject,
    getProjectIDs,
    setSamples
  }
}
