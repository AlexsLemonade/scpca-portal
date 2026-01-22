import { useContext, useEffect, useState } from 'react'
import { MyDatasetContext } from 'contexts/MyDatasetContext'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useDataset } from 'hooks/useDataset'
import { allModalities } from 'config/datasets'
import { uniqueArray } from 'helpers/uniqueArray'

export const useMyDataset = () => {
  const {
    myDataset,
    setMyDataset,
    prevMyDatasetFormat,
    setPrevMyDatasetFormat,
    datasets,
    setDatasets,
    setEmail,
    errors,
    setErrors,
    userFormat,
    setUserFormat
  } = useContext(MyDatasetContext)
  const { token, email } = useScPCAPortal()
  const {
    create,
    get,
    update,
    getDatasetProjectData,
    getModalitySamplesDifference,
    getProjectModalitySamplesById,
    getDatasetProjectDataSamples,
    getDatasetProjectSamples,
    getRemainingProjectSampleIds: baseGetRemainingProjectSampleIds,
    isProjectIncludeBulk: baseIsProjectIncludeBulk,
    isProjectMerged: baseIsProjectMerged,
    hasAllProjectSamplesAdded: baseHasAllProjectSamplesAdded,
    hasRemainingProjectSamples: baseHasRemainingProjectSamples
  } = useDataset()

  const emptyDatasetProjectOptions = {
    includeBulk: false,
    includeMerge: false,
    modalities: []
  }

  const [defaultProjectOptions, setDefaultProjectOptions] = useState(
    emptyDatasetProjectOptions
  )

  // Clear dataset format once data is emptied
  useEffect(() => {
    if (!isDatasetDataEmpty) return
    setMyDataset((prev) => ({ ...prev, format: '' }))
  }, [isDatasetDataEmpty])

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

  const createMyDataset = async (dataset) => {
    if (!dataset.format) {
      return addError('A format is required to create a dataset.')
    }

    const newDataset = await create(dataset, token)

    // TODO: Revise once error handling is finalized
    if (newDataset === null) {
      return addError('An error occurred while trying to create a new dataset.')
    }

    setMyDataset(newDataset)
    setPrevMyDatasetFormat(newDataset.format) // Use to compare format changes on myDataset replace
    // Add the newly generated dataset ID for historical record
    setDatasets((prev) =>
      prev.includes(newDataset.id) ? prev : [...prev, newDataset.id]
    )

    return newDataset
  }

  const getMyDataset = async (downloadToken = '') => {
    if (!myDataset.id) return null

    // A valid API token is required for dataset file downloads
    const latestDataset = await get(myDataset, downloadToken)

    // TODO: Revise once error handling is finalized
    if (latestDataset === null) {
      return addError('An error occurred while trying to fetch the dataset')
    }

    setMyDataset(latestDataset)

    return latestDataset
  }

  const getMyDatasetCopy = (dataToCopy = myDataset) =>
    structuredClone(dataToCopy) || {}

  const saveMyDataset = async (dataset) =>
    !myDataset.id ? createMyDataset(dataset) : updateMyDataset(dataset)

  const updateMyDataset = async (dataset) => {
    const updatedDataset = await update(dataset)

    // TODO: Revise once error handling is finalized
    if (updatedDataset === null) {
      return addError('An error occurred while trying to update the dataset')
    }

    // Clear myDataset if 'start' flag to ture
    setMyDataset(updatedDataset.start ? {} : updatedDataset)

    return updatedDataset
  }

  const clearMyDataset = async () => updateMyDataset({ ...myDataset, data: {} })

  // Return the flags based on a project modality samples' value (SINGLE_CELL, SPATIAL)
  const getModalityState = (value = []) => ({
    isMerged: value === 'MERGED',
    isNonEmptyArray: Array.isArray(value) && value.length > 0,
    isEmptyArray: Array.isArray(value) && value.length === 0
  })

  const getMergedIncludesBulk = (projectId, dataset) =>
    myDataset.data[projectId]?.includes_bulk ||
    dataset.data[projectId]?.includes_bulk ||
    false

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
      return getProjectModalitySamplesById(projectId, modality)
    }

    return uniqueArray(original, incoming)
  }

  // Handle merging the shared dataset data into myDataset for the UI
  const getMergeMyDatasetData = async (dataset) => {
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

    return mergedProjectModaliies.reduce((acc, [pId, modalityData]) => {
      acc[pId] = {
        ...modalityData,
        includes_bulk: getMergedIncludesBulk(pId, dataset)
      }
      return acc
    }, {})
  }

  const processMyDataset = async () => {
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
    return updateMyDataset({ ...myDataset, email, start: true })
  }

  /* Project-level */
  const addProjectToMyDataset = async (project, newProjectData, format) => {
    const datasetDataCopy = getMyDatasetCopy(myDataset.data)

    // Make sure data is defined for a new dataset
    datasetDataCopy[project.scpca_id] = newProjectData

    const updatedDataset = {
      ...myDataset,
      data: datasetDataCopy,
      format // Required for a new dataset
    }

    return saveMyDataset(updatedDataset)
  }

  const getMyDatasetProjectData = (project) =>
    getDatasetProjectData(myDataset, project)

  const getMyDatasetProjectDataSamples = (project) =>
    getDatasetProjectDataSamples(myDataset, project)

  const getMyDatasetProjectSamples = (project) =>
    getDatasetProjectSamples(myDataset, project)

  const getBuildMyDatasetProjectData = (
    project,
    selectedModalities,
    singleCellSamples,
    spatialSamples
  ) => {
    // Populate modality samples for the project data for addProjectToMyDataset
    const datasetProjectDataCopy = getMyDatasetCopy(
      getMyDatasetProjectData(project)
    )

    const hasModality = (m) => selectedModalities.includes(m)

    datasetProjectDataCopy.SINGLE_CELL =
      hasModality('SINGLE_CELL') || singleCellSamples.length > 0
        ? singleCellSamples
        : []
    datasetProjectDataCopy.SPATIAL =
      hasModality('SPATIAL') || spatialSamples.length > 0 ? spatialSamples : []

    return datasetProjectDataCopy
  }

  // Return remaining project sample IDs of the given project
  const getRemainingProjectSampleIds = (project) =>
    baseGetRemainingProjectSampleIds(myDataset, project)

  const hasAllProjectSamplesAdded = (project) =>
    baseHasAllProjectSamplesAdded(myDataset, project)

  const hasRemainingProjectSamples = (project) =>
    baseHasRemainingProjectSamples(myDataset, project)

  const isProjectIncludeBulk = (project) =>
    baseIsProjectIncludeBulk(myDataset, project)

  const isProjectMerged = (project) => baseIsProjectMerged(myDataset, project)

  const removeProjectByIdFromMyDataset = (projectId) => {
    const datasetCopy = getMyDatasetCopy(myDataset)
    delete datasetCopy.data[projectId]

    return updateMyDataset(datasetCopy)
  }

  /* Sample-level */
  const setMyDatasetSamples = async (project, newProjectData, format) => {
    const datasetDataCopy = getMyDatasetCopy(myDataset.data)

    delete datasetDataCopy[project.scpca_id]
    // Only add projects with requested samples
    if (
      newProjectData.SINGLE_CELL?.length > 0 ||
      newProjectData.SPATIAL?.length > 0
    ) {
      datasetDataCopy[project.scpca_id] = newProjectData
    }

    const updatedDataset = {
      ...myDataset,
      data: datasetDataCopy,
      format // Required for a new dataset
    }

    return saveMyDataset(updatedDataset)
  }

  return {
    myDataset,
    setMyDataset,
    prevMyDatasetFormat,
    setPrevMyDatasetFormat,
    datasets,
    email,
    errors,
    userFormat,
    setUserFormat,
    addError,
    removeError,
    defaultProjectOptions,
    isDatasetDataEmpty,
    clearMyDataset,
    createMyDataset,
    getMyDataset,
    saveMyDataset,
    updateMyDataset,
    getMergeMyDatasetData,
    processMyDataset,
    addProjectToMyDataset,
    removeProjectByIdFromMyDataset,
    getMyDatasetProjectData,
    getMyDatasetProjectDataSamples,
    getMyDatasetProjectSamples,
    getBuildMyDatasetProjectData,
    getRemainingProjectSampleIds,
    hasAllProjectSamplesAdded,
    hasRemainingProjectSamples,
    isProjectIncludeBulk,
    isProjectMerged,
    setMyDatasetSamples,
    getModalitySamplesDifference
  }
}
