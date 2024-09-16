import { getAPIUrl } from 'helpers/getAPIUrl'
import { request } from 'helpers/request'

export const filters = [
  'project__id',
  'sample__id',
  'id',
  'modality',
  'format',
  'portal_metadata_only'
]

const computedFiles = {
  get: (id, authorization) =>
    request(getAPIUrl(`computed-files/${id}`), { authorization }),
  list: (query) => request(getAPIUrl('computed-files', query))
}

export default computedFiles
