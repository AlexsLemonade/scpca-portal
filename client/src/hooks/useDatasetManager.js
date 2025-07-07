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

  /* Dataset Configs */
  const saveFormat = (format) => {
    // Sets the download format only when creating a new dataset.
    setUserFormat(format)
  }

  /* Dataset-level */
  const clearDataset = async (dataset) => {
    const updatedDataset = await updateDataset({ ...dataset, data: {} })
    return updatedDataset
  }

  const createDataset = async (dataset) => {
    const newDataset = await api.datasets.create(dataset, token)
    return newDataset
  }

  const getDataset = async (dataset) => {
    // A valid API token is required for dataset file downloads.
    const latestDataset = await api.datasets.get(dataset.id, token)
    return latestDataset
  }

  const processDataset = async (dataset) => {
    const latestDataset = !dataset.id
      ? await createDataset(dataset)
      : await updateDataset(dataset)
    return latestDataset
  }

  const updateDataset = async (dataset) => {
    const latestDataset = await api.datasets.update(dataset.id, dataset, token)
    return latestDataset
  }

  /* Project-level */
  const addProject = async (dataset, project, modalities = []) => {
    const updatedDataset = !dataset.id
      ? await createDataset(dataset)
      : await updateDataset(dataset)
    return updatedDataset
  }

  const removeProject = async (dataset, project, modalities = []) => {
    const updatedDataset = await updateDataset(dataset.id, dataset)
    return updatedDataset
  }

  // Single-cell only
  const mergeProject = async (dataset, project, modality = 'SINGLE_CELL') => {
    const updatedDataset = !dataset.id
      ? await createDataset(dataset)
      : await updateDataset(dataset)
    return updatedDataset
  }

  // Single-cell only
  const unmergeProject = async (dataset, project, modality = 'SINGLE_CELL') => {
    const updatedDataset = await updateDataset(dataset.id, dataset)
    return updatedDataset
  }

  const getProjectIDs = (dataset) => Object.keys(dataset.data)

  /* Sample-level */
  const addSamples = async (dataset, project, modality, samples) => {
    const updatedDataset = !dataset.id
      ? await createDataset(dataset)
      : await updateDataset(dataset)
    return updatedDataset
  }

  const removeSamples = async (dataset, project, modality, samples) => {
    const updatedDataset = await updateDataset(dataset.id, dataset)
    return updatedDataset
  }

  return {
    myDataset,
    datasets,
    email,
    setEmail,
    userFormat,
    clearDataset,
    createDataset,
    getDataset,
    processDataset,
    updateDataset,
    addProject,
    removeProject,
    mergeProject,
    unmergeProject,
    getProjectIDs,
    addSamples,
    removeSamples
  }
}
