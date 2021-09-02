import getAPIUrl from 'helpers/getAPIUrl'
import request from 'helpers/request'

const apiToken = {
  create: (token) =>
    request(getAPIUrl(`tokens`), {
      method: 'POST',
      body: JSON.stringify(token)
    }),
  get: (authorization) =>
    request(getAPIUrl(`tokens/${authorization}`), { authorization }),
  update: (authorization, token) =>
    request(getAPIUrl(`tokens/${authorization}`), {
      authorization,
      method: 'PUT',
      body: JSON.stringify(token)
    })
}

export default apiToken
