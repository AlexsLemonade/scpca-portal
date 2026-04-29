import { getAPIUrl } from 'helpers/getAPIUrl'
import { request } from 'helpers/request'

export const filters = [
  'project__id',
  'id',
  'has_cite_seq_data',
  'scpca_sample_id',
  'technologies',
  'diagnosis',
  'subdiagnosis',
  'age',
  'age_timing',
  'sex',
  'disease_timing',
  'tissue_location',
  'treatment',
  'seq_units'
]

const samples = {
  get: (id) => request(getAPIUrl(`samples/${id}`)),
  list: (query) => request(getAPIUrl('samples', query))
}

export default samples
