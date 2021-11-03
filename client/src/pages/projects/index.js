import React from 'react'
import { useRouter } from 'next/router'
import { Anchor, Box, Grid, Text } from 'grommet'
import { ProjectSearchResult } from 'components/ProjectSearchResult'
import { ProjectSearchFilter } from 'components/ProjectSearchFilter'
import { ProjectSearchFilterPills } from 'components/ProjectSearchFilterPills'
import { ScPCAPortalContext } from 'contexts/ScPCAPortalContext'
import { api } from 'api'

const Project = ({ projects, count, filters, filterOptions }) => {
  const { browseFilters, setBrowseFilters } = React.useContext(
    ScPCAPortalContext
  )
  if (!projects) return '404'
  const router = useRouter()

  React.useEffect(() => {
    setBrowseFilters(filters)
  }, [])

  const onFilterChange = async (newFilters) => {
    setBrowseFilters(newFilters)
    router.replace({
      pathname: '/projects',
      query: newFilters
    })
  }

  const hasFilters = Object.keys(browseFilters).length > 0
  const clearFilters = () => {
    onFilterChange({})
  }

  return (
    <Box width="full">
      <Box pad={{ bottom: 'large' }}>
        <Text serif size="xlarge">
          Browse Projects
        </Text>
      </Box>
      <Grid
        rows={['auto']}
        columns={['small', 'auto']}
        areas={[
          { name: 'filters', start: [0, 0], end: [0, 0] },
          { name: 'results', start: [1, 0], end: [1, 0] }
        ]}
        direction="row"
        gap="large"
      >
        <Box gridArea="filters" width="small">
          <Box direction="row" justify="between">
            <Text serif size="large">
              Filters
            </Text>
            <Anchor
              color="brand"
              label="clear all"
              disabled={!hasFilters}
              onClick={clearFilters}
            />
          </Box>
          <ProjectSearchFilter
            filters={browseFilters}
            filterOptions={filterOptions}
            onFilterChange={onFilterChange}
          />
        </Box>
        <Box gridArea="results">
          <Box direction="row" justify="between">
            <Box flex="shrink">
              <ProjectSearchFilterPills
                filters={browseFilters}
                onFilterChange={onFilterChange}
              />
            </Box>
            <Box flex="grow">
              <Text alignSelf="end">Number of Projects: {count}</Text>
            </Box>
          </Box>
          {projects.map((p) => (
            <Box key={p.scpca_id} margin={{ top: 'medium', bottom: 'small' }}>
              <ProjectSearchResult project={p} />
            </Box>
          ))}
        </Box>
      </Grid>
    </Box>
  )
}

export const getServerSideProps = async ({ query }) => {
  const [projectRequest, optionsRequest] = await Promise.all([
    api.projects.list(query),
    api.options.projects.get()
  ])

  if (projectRequest.isOk && optionsRequest.isOk) {
    const { results: projects, count } = projectRequest.response
    const filterOptions = optionsRequest.response

    return {
      props: { projects, count, filters: query, filterOptions }
    }
  }

  return { props: { project: null } }
}

export default Project
