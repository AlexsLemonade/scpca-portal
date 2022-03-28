import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { Anchor, Box, Grid, Text } from 'grommet'
import { ProjectSearchResult } from 'components/ProjectSearchResult'
import { ProjectSearchFilter } from 'components/ProjectSearchFilter'
import { ProjectSearchFilterPills } from 'components/ProjectSearchFilterPills'
import { ResponsiveSheet } from 'components/ResponsiveSheet'
import { useScPCAPortal } from 'hooks/useScPCAPortal'
import { useResponsive } from 'hooks/useResponsive'
import { delay } from 'helpers/delay'
import { api } from 'api'
import Error from 'pages/_error'

const Project = ({ projects, count, filters, filterOptions }) => {
  const { browseFilters, setBrowseFilters } = useScPCAPortal()
  const { responsive } = useResponsive()
  const [showFilters, setShowFilters] = useState(false)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  // we don't want to 404 here we want to show that the api is down
  if (!projects) return <Error />

  useEffect(() => {
    setBrowseFilters(filters)
  }, [])

  const onFilterChange = async (newFilters) => {
    setLoading(true)
    setBrowseFilters(newFilters)
    await Promise.all([
      router.replace({
        pathname: '/projects',
        query: newFilters
      }),
      delay(1200)
    ])
    setLoading(false)
  }

  const hasFilters = Object.keys(browseFilters).length > 0
  const clearFilters = () => {
    onFilterChange({})
  }

  return (
    <Box width="full" pad={responsive({ horizontal: 'medium' })}>
      <Box pad={{ bottom: 'large' }}>
        <Text serif size="xlarge">
          Browse Projects
        </Text>
      </Box>
      <Grid
        rows={responsive(['auto', 'auto'], ['auto'])}
        columns={responsive(['auto'], ['small', 'auto'])}
        areas={responsive(
          [
            { name: 'filters', start: [0, 0], end: [0, 0] },
            { name: 'results', start: [0, 1], end: [0, 1] }
          ],
          [
            { name: 'filters', start: [0, 0], end: [0, 0] },
            { name: 'results', start: [1, 0], end: [1, 0] }
          ]
        )}
        direction="row"
        gap="large"
      >
        <Box gridArea="filters">
          <ResponsiveSheet
            show={showFilters}
            setShow={setShowFilters}
            label="Show Filters"
            loading={loading}
          >
            <Box width="small">
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
          </ResponsiveSheet>
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
