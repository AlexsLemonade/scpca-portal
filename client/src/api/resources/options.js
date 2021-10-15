import { getAPIUrl } from 'helpers/getAPIUrl'
import { request } from 'helpers/request'

const options = {
  projects: {
    get: () => request(getAPIUrl('project-options'))
  }
}

export default options
