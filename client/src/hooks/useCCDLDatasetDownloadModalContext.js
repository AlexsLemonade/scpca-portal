import { useContext, useEffect, useState } from 'react'
import { CCDLDatasetDownloadModalContext } from 'contexts/CCDLDatasetDownloadModalContext'
import { formatNames } from 'config/ccdlDatasets'

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
    downloadLink,
    project,
    datasets,
    token
  } = useContext(CCDLDatasetDownloadModalContext)

  const isTokenReady = !token
  const isOptionsReady = datasets?.length > 1 && !!token && !downloadDataset
  const isDownloadReady = !!downloadDataset && !!token
  const [modalTitle, setModalTitle] = useState('Downloading')

  const modalModalityNames = {
    SINGLE_CELL: 'Data',
    SPATIAL: 'Spatial Data'
  }

  useEffect(() => {
    if (!selectedDataset) return

    const modalTitleAction = isDownloadReady ? 'Downloading' : 'Download'
    const modalityName =
      selectedDataset.format === 'METADATA'
        ? 'Sample Metadata'
        : modalModalityNames[selectedDataset.ccdl_modality]
    const modalTitleResource = selectedDataset.ccdl_project_id
      ? 'Project'
      : `Portal-wide ${modalityName}`
    const asFormat =
      selectedDataset.ccdl_modality === 'SINGLE_CELL'
        ? `as ${formatNames[selectedDataset.format]}`
        : ''

    setModalTitle(
      `${modalTitleAction} ${modalTitleResource} ${asFormat}`.trim()
    )
  }, [selectedDataset])

  return {
    showing,
    setShowing,
    modalTitle,
    isDownloadReady,
    isTokenReady,
    isOptionsReady,
    downloadDataset,
    setDownloadDataset,
    downloadLink,
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
