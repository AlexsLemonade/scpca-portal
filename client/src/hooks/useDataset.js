import { useContext } from 'react'
import { MyDatasetContext } from 'contexts/MyDatasetContext'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { allModalities } from 'config/datasets'
import { differenceArray } from 'helpers/differenceArray'
import { getHashMap } from 'helpers/getHashMap'
import { uniqueArray } from 'helpers/uniqueArray'

export const useDataset = () => {
  const { token, email, setEmail } = useScPCAPortal()
  const { errors, setErrors } = useContext(MyDatasetContext) // TODO: Removed once error handling is finalized

  const getErrorMessage = (statusCode) => {
    const defaultMessage = 'An unexpected error occurred.'
    // TODO: Revise once error handling is finalized (for recoverable errors)
    const exceptions = {
      400: 'Bad Request: Invalid or missing required fields.',
      403: 'Forbidden: API token is missing or invalid.',
      404: 'Not Found: The dataset does not exist or cannot be retrieved.',
      405: 'Method Not Allowed: This method is not allowed for the requested endpoint.',
      409: 'Conflict: Processing datasets cannot be modified.'
    }

    if (statusCode in exceptions) {
      return exceptions[statusCode]
    }

    return defaultMessage
  }

  const create = async (dataset) => {
    if (!dataset.format) {
      setErrors('A format is required to create a dataset.')
      // TODO: Revise once error handling is finalized
      return null
    }

    const datasetRequest = await api.datasets.create(dataset)

    if (!datasetRequest.isOk) {
      setErrors(getErrorMessage(datasetRequest.status))
      // TODO: Revise once error handling is finalized
      return null
    }

    return datasetRequest.response
  }

  const get = async (dataset, downloadToken = '') => {
    const datasetRequest = await api.datasets.get(dataset.id, downloadToken)

    if (!datasetRequest.isOk) {
      setErrors(getErrorMessage(datasetRequest.status))
      // TODO: Revise once error handling is finalized
      return null
    }

    return datasetRequest.response
  }

  const process = async (dataset) => {
    if (!token) {
      setErrors('A valid token is required to process the dataset')
      return null
    }

    if (!email) {
      setErrors('An email is required to process the dataset')
      return null
    }

    const datasetRequest = await update({ ...dataset, email, start: true })

    if (!datasetRequest.isOk) {
      setErrors(getErrorMessage(datasetRequest.status))
      // TODO: Revise once error handling is finalized
      return null
    }

    setEmail(dataset.email)

    return datasetRequest.response
  }

  const regenerate = async (dataset) => {
    if (!token) {
      setErrors('A valid token is required to process the dataset')
      return null
    }

    if (!email) {
      setErrors('An email is required to process the dataset')
      return null
    }

    const datasetRequest = await api.datasets.create({
      ...dataset,
      email,
      start: true
    })

    if (!datasetRequest.isOk) {
      setErrors(getErrorMessage(datasetRequest.status))
      // TODO: Revise once error handling is finalized
      return null
    }

    return datasetRequest.response
  }

  const update = async (dataset) => {
    const datasetRequest = await api.datasets.update(dataset.id, dataset, token)

    if (!datasetRequest.isOk) {
      setErrors(getErrorMessage(datasetRequest.status))
      // TODO: Revise once error handling is finalized
      return null
    }

    return datasetRequest.response
  }

  const isProjectIncludeBulk = (dataset, project) =>
    dataset.data?.[project.scpca_id]?.includes_bulk || false

  const isProjectMerged = (dataset, project) =>
    dataset.data[project.scpca_id].SINGLE_CELL === 'MERGED'

  const getDatasetProjectData = (dataset, project) =>
    dataset?.data?.[project.scpca_id] || {}

  const getDatasetProjectDataSamples = (dataset, project) => {
    // Return added samples in each modalities and
    // unmerge the single-cell samples if they're merged
    const { SINGLE_CELL: singleCell = [], SPATIAL: spatial = [] } =
      getDatasetProjectData(dataset, project)

    return {
      SINGLE_CELL:
        singleCell === 'MERGED'
          ? project.modality_samples.SINGLE_CELL
          : singleCell,
      SPATIAL: spatial
    }
  }

  const getDatasetProjectSamples = (dataset, project) => {
    // Combines modalities and returns an array of all unique samples
    // available for projects that exist the dataset
    const { samples } = project
    const { SINGLE_CELL: mergedOrSingleCellIds, SPATIAL: spatialIds } =
      dataset.data[project.scpca_id]

    const singleCellIds =
      mergedOrSingleCellIds === 'MERGED'
        ? project.modality_samples.SINGLE_CELL
        : mergedOrSingleCellIds

    const sampleIds = uniqueArray(singleCellIds, spatialIds)
    const samplesMap = getHashMap(samples, 'scpca_id')

    return sampleIds.map((id) => samplesMap[id])
  }

  // TODO: Implementation might change
  const getDatasetState = (dataset) => {
    const {
      is_processing: isProcessing,
      is_succeeded: isSucceeded,
      is_failed: isFailed,
      is_terminated: isTerminated,
      is_expired: isExpired
    } = dataset

    const processed = isSucceeded || isFailed || isTerminated

    return {
      isUnprocessed: !isProcessing || !processed,
      isProcessing: isProcessing && !isFailed,
      isFailed,
      isTerminated,
      isReady: isSucceeded && !isExpired,
      isExpired: isSucceeded && isExpired
    }
  }

  const getModalitySamplesDifference = (project, modalities) => {
    if (modalities.length <= 1) return []

    const { modality_samples: modalitySamples } = project

    const selectedModalitySamples = modalities.map((m) => modalitySamples[m])
    const allSamples = uniqueArray(...selectedModalitySamples)

    return allSamples.filter(
      (s) => !selectedModalitySamples.every((m) => m.includes(s))
    )
  }

  const getProjectModalitySamplesById = async (projectId, modality) => {
    const { isOk, response } = await api.projects.get(projectId)
    return isOk ? response.modality_samples[modality] : null
  }

  const getRemainingProjectSampleIds = (dataset, project) => {
    // Returns remaining project sample IDs that haven't been included
    // in the given project present in the dataset
    const projectData = getDatasetProjectData(dataset, project)

    if (Object.keys(projectData).length === 0) {
      return allModalities.reduce((acc, m) => {
        acc[m] = project.modality_samples[m]
        return acc
      }, {})
    }

    return allModalities.reduce((acc, m) => {
      const addedSampleId = projectData[m]

      if (addedSampleId === 'MERGED') {
        acc[m] = []
      } else {
        // Exclude multiplexed samples for datasets in AnnData format
        const isMultiplexedExcluded =
          dataset.format === 'ANN_DATA' && project.has_multiplexed_data

        const projectModalitySampleIds = isMultiplexedExcluded
          ? differenceArray(
              project.modality_samples[m],
              project.multiplexed_samples
            )
          : project.modality_samples[m]

        acc[m] = differenceArray(projectModalitySampleIds, addedSampleId)
      }
      return acc
    }, {})
  }

  const hasAllProjectSamplesAdded = (dataset, project) => {
    if (!dataset.data?.[project.scpca_id]) {
      return false
    }

    const remamingSamples = getRemainingProjectSampleIds(dataset, project)

    return allModalities.every((m) => remamingSamples[m].length === 0)
  }

  const hasRemainingProjectSamples = (dataset, project) => {
    if (!dataset.data?.[project.scpca_id]) {
      return false
    }

    const remamingSamples = getRemainingProjectSampleIds(dataset, project)

    return allModalities.some((m) => remamingSamples[m].length > 0)
  }

  return {
    errors,
    create,
    get,
    process,
    regenerate,
    update,
    isProjectIncludeBulk,
    isProjectMerged,
    getDatasetProjectData,
    getDatasetProjectDataSamples,
    getDatasetProjectSamples,
    getDatasetState,
    getModalitySamplesDifference,
    getProjectModalitySamplesById,
    getRemainingProjectSampleIds,
    hasAllProjectSamplesAdded,
    hasRemainingProjectSamples
  }
}
