import { getAPIUrl } from 'helpers/getAPIUrl'
import { request } from 'helpers/request'

const ccdlDatasets = {
  get: (id, authorization) =>
    request(getAPIUrl(`ccdl-datasets/${id}`), { authorization }), // token required for file downloads
  list: (query) => request(getAPIUrl('ccdl-datasets', query))
}

export default ccdlDatasets
