import { useContext, useEffect, useState } from 'react'
import { CCDLDatasetDownloadModalContext } from 'contexts/CCDLDatasetDownloadModalContext'
import { getReadable } from 'helpers/getReadable'

export const useCCDLDatasetDownloadModalContext = () => {
  const {
    showing,
    setShowing,
    modality,
    setModality,
    format,
    setFormat,
    includesMerged,
    setIncludesMerged,
    excludeMultiplexed,
    setExcludeMultiplexed,
    selectedDataset,
    isMergedObjectsAvailable,
    isMultiplexedAvailable,
    modalityOptions,
    formatOptions,
    downloadDataset,
    setDownloadDataset,
    downloadableDataset,
    project,
    datasets,
    token
  } = useContext(CCDLDatasetDownloadModalContext)

  const isTokenReady = !token
  const isOptionsReady = datasets?.length > 1 && !!token && !downloadDataset
  const isDownloadReady = !!downloadableDataset && !!token

  const modalTitleAction =
    isTokenReady || isOptionsReady ? 'Download' : 'Downloading'
  const [modalTitle, setModalTitle] = useState(modalTitleAction)

  const modalModalityNames = {
    SINGLE_CELL: 'Data',
    SPATIAL: 'Spatial Data'
  }

  useEffect(() => {
    if (!selectedDataset) return

    const modalityName =
      selectedDataset.format === 'METADATA'
        ? 'Sample Metadata'
        : modalModalityNames[selectedDataset.ccdl_modality]
    const modalTitleResource = selectedDataset.ccdl_project_id
      ? 'Project'
      : `Portal-wide ${modalityName}`
    const asFormat =
      !selectedDataset.ccdl_project_id &&
      selectedDataset.ccdl_modality === 'SINGLE_CELL'
        ? `as ${getReadable(selectedDataset.format)}`
        : ''

    setModalTitle(
      `${modalTitleAction} ${modalTitleResource} ${asFormat}`.trim()
    )
  }, [selectedDataset, modalTitleAction])

  return {
    showing,
    setShowing,
    modalTitle,
    isDownloadReady,
    isTokenReady,
    isOptionsReady,
    downloadDataset,
    setDownloadDataset,
    downloadableDataset,
    modality,
    setModality,
    format,
    setFormat,
    includesMerged,
    setIncludesMerged,
    excludeMultiplexed,
    setExcludeMultiplexed,
    selectedDataset,
    isMergedObjectsAvailable,
    isMultiplexedAvailable,
    modalityOptions,
    formatOptions,
    project,
    datasets
  }
}
