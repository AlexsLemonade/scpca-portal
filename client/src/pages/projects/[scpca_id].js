import React from 'react'
import { Box, Tabs, Tab, Text } from 'grommet'
import { ProjectHeader } from 'components/ProjectHeader'
import { DetailsTable } from 'components/DetailsTable'
import { ProjectSamplesTable } from 'components/ProjectSamplesTable'
import { ProjectSamplesSummaryTable } from 'components/ProjectSamplesSummaryTable'
import api from 'api'

const Project = ({ project }) => {
  if (!project) return '404'

  return (
    <Box width="xlarge">
      <ProjectHeader project={project} />
      <Box pad={{ vertical: 'large' }}>
        <Tabs>
          <Tab title="Project Details">
            <Box pad={{ vertical: 'large' }}>
              <DetailsTable
                data={project}
                order={[
                  'abstract',
                  'disease_timings',
                  'sample_count',
                  'human_readable_pi_name'
                ]}
              />
            </Box>
            <Text weight="bold">Sample Summary</Text>
            <ProjectSamplesSummaryTable summaries={project.summaries} />
          </Tab>
          <Tab title="Sample Details">
            <ProjectSamplesTable samples={project.samples} />
          </Tab>
        </Tabs>
      </Box>
    </Box>
  )
}

export const getServerSideProps = async ({ query }) => {
  const projectRequest = await api.projects.get(query.scpca_id)

  if (projectRequest.isOk) {
    const project = projectRequest.response
    return {
      props: { project }
    }
  }

  return { props: { project: null } }
}

export default Project
