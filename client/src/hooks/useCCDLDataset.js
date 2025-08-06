import { useEffect, useState } from 'react'
import { api } from 'api'

export const useCCDLDataset = (portalWide = false) => {
  const [ccdlDatasets, setCCDLDatasets] = useState([])

  // Set states for the portal metedata
  useEffect(() => {
    const getCCDLDatasets = async () => {
      const resourceRequest = await api.ccdlDatasets.list({
        ccdl_project_id__isnull: portalWide
      })
      const { results } = resourceRequest.response
      setCCDLDatasets(results)
    }

    getCCDLDatasets()
  }, [portalWide])

  return {
    ccdlDatasets
  }
}

export default useCCDLDataset
