import { useContext } from 'react'
import { CCDLDatasetDownloadOptionsContext } from 'contexts/CCDLDatasetDownloadOptionsContext'

export const useCCDLDatasetDownloadOptionsContext = () =>
  useContext(CCDLDatasetDownloadOptionsContext)
