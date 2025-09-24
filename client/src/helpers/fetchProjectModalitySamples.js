import { api } from 'api'
// Fetches samples for a given project ID and modality
export const fetchProjectModalitySamples = async (projectId, modality) => {
  const samplesRequest = await api.samples.list({
    project__scpca_id: projectId,
    limit: 1000 // TODO:: 'all' option
  })

  if (!samplesRequest.isOk) return null

  return samplesRequest.response.results
    .filter((s) => s[`has_${modality.toLowerCase()}_data`])
    .map((s) => s.scpca_id)
}
