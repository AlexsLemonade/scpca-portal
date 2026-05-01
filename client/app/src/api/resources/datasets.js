import { getAPIUrl } from 'helpers/getAPIUrl'
import { request } from 'helpers/request'

const datasets = {
  create: (body, authorization) =>
    request(getAPIUrl(`datasets`), {
      method: 'POST',
      authorization,
      body: JSON.stringify(body)
    }),
  get: (id, authorization) =>
    request(getAPIUrl(`datasets/${id}`), { authorization }), // token required for file downloads
  update: (id, body, authorization) =>
    request(getAPIUrl(`datasets/${id}`), {
      method: 'PUT',
      authorization,
      body: JSON.stringify(body)
    })
}

export default datasets
