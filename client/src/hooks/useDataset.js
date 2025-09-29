import { useContext } from 'react'
import { MyDatasetContext } from 'contexts/MyDatasetContext'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { api } from 'api'
import { uniqueArray } from 'helpers/uniqueArray'

export const useDataset = () => {
  const { token, setEmail } = useScPCAPortal()
  const { errors, addError } = useContext(MyDatasetContext) // TODO: Removed once error handling is finalized

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
      addError('A format is required to create a dataset.')
      // TODO: Revise once error handling is finalized
      return null
    }

    const datasetRequest = await api.datasets.create(dataset)

    if (!datasetRequest.isOk) {
      addError(getErrorMessage(datasetRequest.status))
      // TODO: Revise once error handling is finalized
      return null
    }

    return datasetRequest.response
  }

  const get = async (dataset, downloadToken = '') => {
    const datasetRequest = await api.datasets.get(dataset.id, downloadToken)

    if (!datasetRequest.isOk) {
      addError(getErrorMessage(datasetRequest.status))
      // TODO: Revise once error handling is finalized
      return null
    }

    return datasetRequest.response
  }

  const process = async (dataset) => {
    if (!token) {
      addError('A valid token is required to process the dataset')
      return null
    }

    if (!dataset.email) {
      addError('An email is required to process the dataset')
      return null
    }

    const datasetRequest = await update({ ...dataset, start: true })

    if (!datasetRequest.isOk) {
      addError(getErrorMessage(datasetRequest.status))
      // TODO: Revise once error handling is finalized
      return null
    }

    setEmail(dataset.email)

    return datasetRequest.response
  }

  const update = async (dataset) => {
    const datasetRequest = await api.datasets.update(dataset.id, dataset, token)

    if (!datasetRequest.isOk) {
      addError(getErrorMessage(datasetRequest.status))
      // TODO: Revise once error handling is finalized
      return null
    }

    return datasetRequest.response
  }

  const isProjectIncludeBulk = (dataset, project) =>
    dataset.data?.[project.scpca_id]?.includes_bulk || false

  const isProjectMerged = (dataset, project) =>
    dataset.data[project.scpca_id].SINGLE_CELL === 'MERGED'

  // Return an array of all samples in the project data
  const getDatasetProjectSamples = (dataset, project) => {
    const { samples } = project
    const { SINGLE_CELL: singleCell, SPATIAL: spatial } =
      dataset.data[project.scpca_id]

    const singleCellSamples =
      singleCell === 'MERGED'
        ? samples.filter((s) => s.has_single_cell_data)
        : samples.filter(
            (s) => s.has_single_cell_data && singleCell.includes(s.scpca_id)
          )
    const spatialSamples = samples.filter(
      (s) => s.has_spatial_data && spatial.includes(s.scpca_id)
    )

    return uniqueArray(singleCellSamples, spatialSamples)
  }

  // TODO: Implementation might change
  const getDatasetState = (dataset) => {
    const {
      is_pending: isPending = true, // TEMP for UI demo
      is_processing: isProcessing,
      is_succeeded: isSucceeded,
      is_failed: isFailed,
      is_terminated: isTerminated,
      is_expired: isExpired
    } = dataset

    const processingStarted =
      isProcessing || isSucceeded || isFailed || isTerminated

    return {
      isUnprocessed: isPending && !processingStarted,
      isProcessing: isProcessing && !isFailed,
      isFailed,
      isTerminated,
      isReady: isSucceeded && !isExpired,
      isExpired: isSucceeded && isExpired
    }
  }

  return {
    errors,
    create,
    get,
    process,
    update,
    isProjectIncludeBulk,
    isProjectMerged,
    getDatasetProjectSamples,
    getDatasetState
  }
}
