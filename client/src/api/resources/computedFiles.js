import getAPIUrl from 'helpers/getAPIUrl'
import request from 'helpers/request'

export const filters = ['project__id', 'sample__id', 'id', 'type']

const computedFiles = {
  get: (id, authorization) =>
    request(getAPIUrl(`computed-files/${id}`, { authorization })),
  list: (query) => request(getAPIUrl('computed-files', query))
}

export default computedFiles
