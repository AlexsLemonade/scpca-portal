import { useContext } from 'react'
import { CCDLDatasetDownloadOptionsContext } from 'contexts/CCDLDatasetDownloadOptionsContext'

export const useCCDLDatasetDownloadOptions = () =>
  useContext(CCDLDatasetDownloadOptionsContext)
