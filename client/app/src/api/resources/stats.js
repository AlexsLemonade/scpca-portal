import { getAPIUrl } from 'helpers/getAPIUrl'
import { request } from 'helpers/request'

const stats = {
  get: () => request(getAPIUrl('stats'))
}

export default stats
