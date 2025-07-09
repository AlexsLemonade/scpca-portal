// Temporarily added for linter
/* eslint-disable no-unused-vars */
import { useContext } from 'react'
import { DatasetManagerContext } from 'contexts/DatasetManagerContext'
import { api } from 'api'
import { useScPCAPortal } from './useScPCAPortal'

export const useDatasetManager = () => {
  const { myDataset, setMyDataset, datasets, setDatasets, email, setEmail } =
    useContext(DatasetManagerContext)
  const { token, userFormat, setUserFormat } = useScPCAPortal()

  /* Dataset-level */
  const clearDataset = async (dataset) => {
    const updatedDataset = await updateDataset({ ...dataset, data: {} })
    return updatedDataset
  }

  const createDataset = async (dataset) => {
    // Asserts that format is defined and save if defined
    const newDataset = await api.datasets.create(dataset, token)
    // If success, update myDataset
    return newDataset
  }

  const getDataset = async (dataset) => {
    // A valid API token is required for dataset file downloads
    const latestDataset = await api.datasets.get(dataset.id, token)
    // If success, updates myDataset
    return latestDataset
  }

  const processDataset = async (dataset) => {
    // Sets the start flag to true to process the dataset
    const latestDataset = !dataset.id
      ? await createDataset(dataset)
      : await updateDataset(dataset)
    // If success, removes myDataset(no longer editable)
    return latestDataset
  }

  const updateDataset = async (dataset) => {
    const latestDataset = await api.datasets.update(dataset.id, dataset, token)
    // If success, updates myDataset
    return latestDataset
  }

  /* Project-level */
  const addProject = async (dataset, project, projectData = {}) => {
    // Copies the dataset before mutation
    // Appends projectData to the specified project in dataset.data
    const updatedDataset = !dataset.id
      ? await createDataset(dataset)
      : await updateDataset(dataset)
    return updatedDataset
  }

  const getProjectData = (project, modality, merged = false) => {
    // Returns an object that would populate dataset.data.[project.scpca_id]
    const dataSlice = {}
    dataSlice[modality] = merged
      ? 'MERGED'
      : project.samples.filter((s) => s.has_modality).map((s) => s.sample_id)
    return dataSlice
  }

  const getProjectIDs = (dataset) => Object.keys(dataset.data)

  const removeProject = async (dataset, project) => {
    // Copies the dataset before mutation
    // Removes the speficied project from dataset.data
    const updatedDataset = await updateDataset(dataset.id, dataset)
    return updatedDataset
  }

  /* Sample-level */
  const setSamples = async (dataset, project, modality, updatedSamples) => {
    // 'updatedSamples' is either sampleIDs[] or 'MERGE'
    const updatedDataset = !dataset.id
      ? await createDataset(dataset)
      : await updateDataset(dataset)
    return updatedDataset
  }

  return {
    myDataset,
    datasets,
    email,
    userFormat,
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
