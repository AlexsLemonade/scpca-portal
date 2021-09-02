import getAPIUrl from 'helpers/getAPIUrl'
import request from 'helpers/request'

export const fitlers = [
  'id',
  'pi_name',
  'has_bulk_rna_seq',
  'title',
  'abstract',
  'technologies',
  'diagnoses',
  'seq_units',
  'disease_timings'
]

const projects = {
  get: (id) => request(getAPIUrl(`projects/${id}`)),
  list: (query) => request(getAPIUrl('projects', query))
}

export default projects
